from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from labbench_comm.protocols.packet import Packet


class DeviceMessage(ABC):
    """
    Base class for a device message.

    A DeviceMessage represents a one-way message (no request/response pairing),
    typically used for notifications, events, or broadcast messages.
    """

    def __init__(
        self,
        packet: Optional[Packet] = None,
        length: Optional[int] = None,
    ) -> None:
        if packet is not None:
            self._packet = packet
        elif length is not None:
            self._packet = Packet(self.code, length)
        else:
            self._packet = Packet(self.code, 0)

    # ------------------------------------------------------------------
    # Abstract API
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def code(self) -> int:
        """
        Message code (1 byte).
        """
        raise NotImplementedError

    @abstractmethod
    def create_dispatcher(self):
        """
        Create and return a dispatcher for this message.
        """
        raise NotImplementedError

    @abstractmethod
    def dispatch(self, listener: Any) -> None:
        """
        Dispatch this message to a listener.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Packet handling
    # ------------------------------------------------------------------

    def get_packet(self, address: Optional[int] = None) -> bytes:
        """
        Serialize the message packet for transmission.

        If an address is provided, it is applied to the packet.
        """
        if address is not None:
            self._packet.address = address

        return self._packet.to_bytes()

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_send(self) -> None:
        """
        Called before the message is sent.

        Override this method to populate the packet dynamically when
        the message size or content cannot be known at construction time.
        """
        pass

    def on_received(self) -> None:
        """
        Called after the message is received and parsed.

        Override this method to initialize properties from the packet
        if doing so lazily would be expensive.
        """
        pass

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def address(self) -> int:
        """
        Address from the packet, or -1 if addressing is not enabled.
        """
        return self._packet.address if self._packet.address_enabled else -1

    @property
    def packet(self) -> Packet:
        """
        Underlying packet for this message.
        """
        return self._packet
