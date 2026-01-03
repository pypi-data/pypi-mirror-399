from __future__ import annotations

from typing import Callable

from labbench_comm.protocols.packet import Packet
from labbench_comm.protocols.device_function import DeviceFunction


class FunctionDispatcher:
    """
    Dispatcher for device functions.

    Maps a function code to a factory that creates a DeviceFunction
    instance and initializes it from a request packet.
    """

    def __init__(
        self,
        code: int,
        creator: Callable[[], DeviceFunction],
    ) -> None:
        self.code = code
        self._creator = creator

    def create(self, packet: Packet) -> DeviceFunction:
        """
        Create and initialize a DeviceFunction from a request packet.

        This is typically used on the slave side when a request
        packet is received.
        """
        func = self._creator()
        func.set_request(packet)
        func.on_slave_received()
        return func
