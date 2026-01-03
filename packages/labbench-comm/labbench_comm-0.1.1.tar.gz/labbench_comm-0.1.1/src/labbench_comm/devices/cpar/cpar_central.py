from __future__ import annotations

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

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def get_peripheral_error_string(self, error_code: int) -> str:
        try:
            return str(EcpError(error_code))
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

        self.state = message.system_state

        for cb in self.status_received:
            cb(self, message)

    def on_event_message(self, message: EventMessage) -> None:
        if message is None:
            return

        for cb in self.event_received:
            cb(self, message)

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
