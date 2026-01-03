import asyncio
from typing import Optional, Any

from labbench_comm.protocols.frame import Frame
from labbench_comm.protocols.destuffer import Destuffer
from labbench_comm.protocols.packet import Packet
from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.device_message import DeviceMessage
from labbench_comm.protocols.message_dispatcher import MessageDispatcher
from labbench_comm.protocols.exceptions import (
    PeripheralNotRespondingError,
    FunctionNotAcknowledgedError,
    PacketFormatError,
)


class BusCentral:
    """
    Asyncio-based coordinator for device communication.

    Responsibilities:
    - Serialize function execution
    - Handle request/response matching
    - Dispatch unsolicited messages
    - Enforce timeouts
    """

    def __init__(self, connection) -> None:
        self._device = None
        self._connection = connection

        self._destuffer = Destuffer()
        self._destuffer.on_receive(self._handle_incoming_frame)
        self._connection.attach_destuffer(self._destuffer)

        self.timeout_ms: int = 500
        self.message_listener: Optional[Any] = None

        self._dispatchers: dict[int, MessageDispatcher] = {}

        self._current_function: Optional[DeviceFunction] = None
        self._current_exception: Optional[Exception] = None

        self._completion_event = asyncio.Event()
        self._lock = asyncio.Lock()

    def attach_device(self, device) -> None:
        self._device = device
        self.message_listener = device

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        await self._connection.open()

    async def close(self) -> None:
        await self._connection.close()

    @property
    def is_open(self) -> bool:
        return self._connection.is_open

    # ------------------------------------------------------------------
    # Function execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        function: DeviceFunction,
        address: Optional[int] = None,
    ) -> None:
        if function is None:
            return

        if not self.is_open:
            raise RuntimeError("Connection is not open")

        async with self._lock:
            self._completion_event.clear()
            self._current_function = function
            self._current_exception = None

            try:
                await self._send_request(function, address)

                await asyncio.wait_for(
                    self._completion_event.wait(),
                    timeout=self.timeout_ms / 1000.0,
                )

            except asyncio.TimeoutError:
                raise PeripheralNotRespondingError("No response from device")

            finally:
                # Ensure clean state even on cancellation
                self._completion_event.clear()
                self._current_function = None

            if self._current_exception is not None:
                raise self._current_exception

    async def _send_request(
        self,
        function: DeviceFunction,
        address: Optional[int],
    ) -> None:
        function.on_send()
        request_bytes = function.get_request(address or 0)
        framed = Frame.encode(request_bytes)
        await self._connection.write_bytes(framed)

    # ------------------------------------------------------------------
    # Message sending
    # ------------------------------------------------------------------

    async def send(
        self,
        message: DeviceMessage,
        address: Optional[int] = None,
    ) -> None:
        if not self.is_open or message is None:
            return

        message.on_send()
        framed = Frame.encode(message.get_packet(address))
        await self._connection.write_bytes(framed)

    # ------------------------------------------------------------------
    # Incoming data handling (called from I/O task)
    # ------------------------------------------------------------------

    def _handle_incoming_frame(self, _: Destuffer, frame: bytes) -> None:
        try:
            packet = Packet.from_frame(frame)
        except PacketFormatError:
            return

        if packet.code == 0x00:
            self._handle_error_packet(packet)
            return

        if packet.is_function:
            self._handle_function_response(packet)
        else:
            self._dispatch_message(packet)

    def _handle_function_response(self, packet: Packet) -> None:
        if self._current_function is None:
            return

        self._current_function.set_response(packet)
        self._current_function.on_received()
        self._completion_event.set()

    def _handle_error_packet(self, packet: Packet) -> None:
        error_code = packet.get_byte(0)
        message = self._device.get_error_string(error_code)
        self._current_exception = FunctionNotAcknowledgedError(message)
        self._completion_event.set()

    # ------------------------------------------------------------------
    # Message dispatch
    # ------------------------------------------------------------------

    def _dispatch_message(self, packet: Packet) -> None:
        dispatcher = self._dispatchers.get(packet.code)
        if dispatcher is None or self.message_listener is None:
            return

        msg = dispatcher.create(packet)
        msg.dispatch(self.message_listener)

    def add_message(self, message: DeviceMessage) -> None:
        if message is None:
            raise ValueError("message must not be None")

        code = message.code
        if code in self._dispatchers:
            raise ValueError(f"Message with code {code} already registered")

        self._dispatchers[code] = message.create_dispatcher()

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.is_open:
            await self.close()
