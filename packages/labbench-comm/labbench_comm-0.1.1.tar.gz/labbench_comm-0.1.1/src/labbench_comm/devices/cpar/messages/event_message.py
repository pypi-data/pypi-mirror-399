from labbench_comm.protocols.device_message import DeviceMessage
from labbench_comm.protocols.message_dispatcher import MessageDispatcher
from labbench_comm.protocols.packet import Packet
from labbench_comm.protocols.exceptions import InvalidMessageError
from labbench_comm.devices.cpar.definitions import EventID


class EventMessage(DeviceMessage):
    @property
    def code(self) -> int:
        return 0x81

    def __init__(self, response: Packet | None = None) -> None:
        if response is not None:
            super().__init__(response)
            if self.packet.length != 1:
                raise InvalidMessageError(
                    "A received EventMessage does not have a length of 1"
                )
        else:
            super().__init__(length=1)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> MessageDispatcher:
        return MessageDispatcher(self.code, lambda p: EventMessage(p))

    def dispatch(self, listener) -> None:
        if hasattr(listener, "on_event_message"):
            listener.on_event_message(self)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def event(self) -> EventID:
        return EventID(self.packet.get_byte(0))

    @event.setter
    def event(self, value: EventID) -> None:
        self.packet.insert_byte(0, int(value))
