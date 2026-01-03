from __future__ import annotations

import asyncio
import logging

from enum import Enum
from typing import Optional

from labbench_comm.protocols.device import Device
from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.functions.device_identification import DeviceIdentification
from labbench_comm.protocols.functions.ping import Ping
from labbench_comm.devices.cpar.messages import (
    StatusMessage,
    EventMessage,
)
from labbench_comm.devices.cpar.definitions import (
    DeviceState,
    EcpError,
)
from labbench_comm.devices.cpar.stimulation_data import (
    StimulationSample,
    StimulationData
)
from labbench_comm.devices.cpar.instruction_codec import InstructionCodec
from labbench_comm.protocols.manufacturer import Manufacturer


class CPARplusCentral(Device):
    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, bus) -> None:
        super().__init__(bus)

        self.baudrate = 38400
        self.retries = 3

        # --- CPAR+ messages ---
        self.add_message(EventMessage())
        self.add_message(StatusMessage())

        # --- Runtime state ---
        self.state: Optional[DeviceState] = None

        self.actual_pressure_01 = 0.0
        self.target_pressure_01 = 0.0
        self.final_pressure_01 = 0.0

        self.actual_pressure_02 = 0.0
        self.target_pressure_02 = 0.0
        self.final_pressure_02 = 0.0

        self.response_connected = False
        self.vas_is_low = False
        self.vas_score = 0.0
        self.final_vas_score = 0.0

        self.status_received = []
        self.event_received = []

        self._ping_task: asyncio.Task | None = None
        self._ping_stop_event = asyncio.Event()
        self._ping_interval: float = 1.0

        self._entered_stimulating = asyncio.Event()
        self._left_stimulating = asyncio.Event()
        self._current_stimulation_data: StimulationData | None = None

        self._logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def get_peripheral_error_string(self, error_code: int) -> str:
        try:
            return str(EcpError(error_code).name)
        except ValueError:
            return f"Unknown CPAR error ({error_code})"

    # ------------------------------------------------------------------
    # Message handlers
    # ------------------------------------------------------------------

    def on_status_message(self, message: StatusMessage) -> None:
        if message is None:
            return

        self.actual_pressure_01 = message.actual_pressure_01
        self.target_pressure_01 = message.target_pressure_01
        self.final_pressure_01 = message.final_pressure_01

        self.actual_pressure_02 = message.actual_pressure_02
        self.target_pressure_02 = message.target_pressure_02
        self.final_pressure_02 = message.final_pressure_02

        self.response_connected = message.vas_connected
        self.vas_is_low = message.vas_is_low
        self.vas_score = message.vas_score
        self.final_vas_score = message.final_vas_score

        previous_state = self.state
        self.state = message.system_state

        # --- state transition tracking ---
        if (
            previous_state != DeviceState.STATE_STIMULATING
            and self.state == DeviceState.STATE_STIMULATING
        ):
            self._entered_stimulating.set()
            self._left_stimulating.clear()
            self._current_stimulation_data = StimulationData()
            self._log.debug("Entered stimulation state, start recording data")
        elif (
            previous_state == DeviceState.STATE_STIMULATING
            and self.state != DeviceState.STATE_STIMULATING
        ):
            self._left_stimulating.set()

        # -----------------------------
        # Collect samples
        # -----------------------------
        if (self.state == DeviceState.STATE_STIMULATING):
            if (self._current_stimulation_data is not None):
                self._current_stimulation_data.add_sample(StimulationSample(
                    actual_pressure_01=message.actual_pressure_01,
                    target_pressure_01=message.target_pressure_01,
                    final_pressure_01=message.final_pressure_01,
                    actual_pressure_02=message.actual_pressure_02,
                    target_pressure_02=message.target_pressure_02,
                    final_pressure_02=message.final_pressure_02,
                    vas_score=message.vas_score,
                    final_vas_score=message.final_vas_score,
                ))  

        for cb in self.status_received:
            cb(self, message)

    def on_event_message(self, message: EventMessage) -> None:
        if message is None:
            return

        for cb in self.event_received:
            cb(self, message)


    async def wait_for_stimulation_complete(self, enter_timeout: float) -> StimulationData:
        """
        Wait until the device enters STATE_STIMULATING and then leaves it.

        :param enter_timeout: seconds to wait for stimulation to start
        :raises StimulationTimeoutError: if stimulation does not start in time
        """

        # Reset state before waiting
        self._entered_stimulating.clear()
        self._left_stimulating.clear()

        # If already stimulating, treat as entered
        if self.state == DeviceState.STATE_STIMULATING:
            self._entered_stimulating.set()

        # --- wait for entry ---
        try:
            await asyncio.wait_for(
                self._entered_stimulating.wait(),
                timeout=enter_timeout,
            )
        except asyncio.TimeoutError as exc:
            raise RuntimeError(
                "Device did not enter STATE_STIMULATING in time"
            ) from exc

        # --- wait for exit ---
        await self._left_stimulating.wait()

        assert self._current_stimulation_data is not None
        return self._current_stimulation_data

    # ------------------------------------------------------------------
    # Deadmans switch for stimulation
    # ------------------------------------------------------------------
    async def start_ping(self, interval: float = 1.0) -> None:
        """
        Start background ping task.

        Calling this multiple times is safe.
        """
        if self._ping_task and not self._ping_task.done():
            return  # already running

        self._ping_interval = interval
        self._ping_stop_event.clear()

        self._ping_task = asyncio.create_task(
            self._ping_loop(),
            name="CPARplusCentral.ping_loop",
        )

    async def stop_ping(self) -> None:
        """
        Stop background ping task.
        """
        if not self._ping_task:
            return

        self._ping_stop_event.set()
        self._ping_task.cancel()

        try:
            await self._ping_task
        except asyncio.CancelledError:
            pass
        finally:
            self._ping_task = None

    async def _ping_loop(self) -> None:
        try:
            while not self._ping_stop_event.is_set():
                try:
                    await self.ping()
                except Exception as exc:
                    self._logger.warning("Background ping failed: %s", exc)

                try:
                    await asyncio.wait_for(
                        self._ping_stop_event.wait(),
                        timeout=self._ping_interval,
                    )
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass

    # ------------------------------------------------------------------
    # Compatibility
    # ------------------------------------------------------------------

    def is_compatible(self, function: DeviceFunction) -> bool:
        if not isinstance(function, DeviceIdentification):
            return False

        return (
            function.manufacturer_id == Manufacturer.InventorsWay
            and function.device_id == 4
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "CPAR+ Device"
