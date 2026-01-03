from labbench_comm.protocols.device_message import DeviceMessage
from labbench_comm.protocols.message_dispatcher import MessageDispatcher
from labbench_comm.protocols.packet import Packet


class PrintfMessage(DeviceMessage):
    """
    Message carrying a debug / printf-style string from a device.
    """

    CODE: int = 0xFF

    @property
    def code(self) -> int:
        return self.CODE

    def __init__(self, packet: Packet | None = None) -> None:
        if packet is not None:
            super().__init__(packet=packet)
        else:
            super().__init__(length=0)

    # ------------------------------------------------------------------
    # Dispatching
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> MessageDispatcher:
        return MessageDispatcher(self.CODE, lambda p: PrintfMessage(p))

    def dispatch(self, listener) -> None:
            if hasattr(listener, "on_printf_message"):
                listener.on_printf_message(self)

    # ------------------------------------------------------------------
    # Message payload
    # ------------------------------------------------------------------

    @property
    def debug_message(self) -> str:
        if self.packet.length > 0:
            return self.packet.get_string(0, self.packet.length)
        return ""

    @debug_message.setter
    def debug_message(self, value: str) -> None:
        if not value:
            self._packet = Packet(self.CODE, 0)
            return

        text = value[:255]  # protocol limit
        encoded_len = len(text)

        self._packet = Packet(self.CODE, encoded_len)
        self._packet.insert_string(0, encoded_len, text)

    def __str__(self) -> str:
        return self.debug_message
