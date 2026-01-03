import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, List

from labbench_comm.protocols.bus_central import BusCentral
from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.device_message import DeviceMessage
from labbench_comm.protocols.functions.device_identification import DeviceIdentification
from labbench_comm.protocols.functions.ping import Ping
from labbench_comm.protocols.error_codes import ErrorCode
from labbench_comm.protocols.exceptions import IncompatibleDeviceError
from labbench_comm.protocols.messages.printf_message import PrintfMessage


class Device(ABC):
    """
    Base class for all devices.

    A Device owns a BusCental and defines:
    - compatibility checks
    - retry policy
    - common functions (ping, identification)
    - message handling
    """

    def __init__(self, central: BusCentral) -> None:
        self.central = central
        self.central.message_listener = self

        self.retries: int = 1
        self.ping_enabled: bool = False

        self.current_address: Optional[int] = None
        self._log = logging.getLogger(__name__)

        central.attach_device(self)
        # Default debug message support
        self.central.add_message(PrintfMessage())

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self.central.is_open

    # ------------------------------------------------------------------
    # Function / message registration
    # ------------------------------------------------------------------

    def add_message(self, message: DeviceMessage) -> None:
        self.central.add_message(message)

    # ------------------------------------------------------------------
    # Ping
    # ------------------------------------------------------------------

    async def ping(self) -> int:
        """
        Ping the connected device.

        Returns the ping counter, or -1 on failure.
        """
        try:
            ping = Ping()
            await self.execute(ping)
            return int(ping.count)
        except asyncio.CancelledError:
            raise
        except Exception:
            return -1

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    @abstractmethod
    def is_compatible(self, function: DeviceFunction) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        if not self.central.is_open:
            await self.central.open()

    async def close(self) -> None:
        if self.central.is_open:
            await self.central.close()

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, function: DeviceFunction) -> None:
        """
        Execute a DeviceFunction with retry handling.
        """
        if function is None:
            return

        if not self.central.is_open:
            raise RuntimeError("Device is not open")

        for attempt in range(self.retries):
            try:
                start = time.monotonic()
                await self.central.execute(function, self.current_address)
                function.transmission_time = int(
                    (time.monotonic() - start) * 1000
                )
                return
            except asyncio.CancelledError:
                raise
            except Exception:
                if attempt == self.retries - 1:
                    raise

    async def send(self, message: DeviceMessage) -> None:
        if message is None:
            return
        await self.central.send(message, self.current_address)

    # ------------------------------------------------------------------
    # Message handlers
    # ------------------------------------------------------------------

    def on_printf_message(self, message: PrintfMessage) -> None:
        self._log.debug(f"DEVICE PRINTF: {message.debug_message}")

    def get_error_string(self, error_code: int) -> str:
        """
        Convert protocol error codes to human-readable strings.
        """
        try:
            code = ErrorCode(error_code)
        except ValueError:
            return self.get_peripheral_error_string(error_code)

        if code is ErrorCode.NO_ERROR:
            return "No error (0x00)"
        if code is ErrorCode.UNKNOWN_FUNCTION_ERR:
            return "Unknown function (0x01)"
        if code is ErrorCode.INVALID_CONTENT_ERR:
            return "Invalid content (0x02)"

        return self.get_peripheral_error_string(error_code)

    @abstractmethod
    def get_peripheral_error_string(self, error_code: int) -> str:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Compatibility helper
    # ------------------------------------------------------------------

    async def identify_and_check(self) -> None:
        ident = self.create_identification_function()
        await self.execute(ident)

        if not self.is_compatible(ident):
            raise IncompatibleDeviceError(str(ident))

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "Generic Device"
