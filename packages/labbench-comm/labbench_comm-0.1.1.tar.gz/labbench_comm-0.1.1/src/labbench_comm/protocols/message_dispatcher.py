from __future__ import annotations

from typing import Callable

from labbench_comm.protocols.packet import Packet
from labbench_comm.protocols.device_message import DeviceMessage


class MessageDispatcher:
    """
    Dispatcher for device messages.

    Maps a message code to a factory function that creates a DeviceMessage
    instance from a received Packet.
    """

    def __init__(
        self,
        code: int,
        creator: Callable[[Packet], DeviceMessage],
    ) -> None:
        if creator is None:
            raise ValueError("creator must not be None")

        self.code = code
        self._creator = creator

    def create(self, packet: Packet) -> DeviceMessage:
        """
        Create and initialize a DeviceMessage from a packet.
        """
        if packet is None:
            raise ValueError("packet must not be None")

        msg = self._creator(packet)
        msg.on_received()
        return msg
