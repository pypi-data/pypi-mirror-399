from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from labbench_comm.protocols.packet import Packet


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------

class DeviceFunctionError(Exception):
    pass


class InvalidMasterRequestError(DeviceFunctionError):
    pass


class InvalidSlaveResponseError(DeviceFunctionError):
    pass


# ----------------------------------------------------------------------
# DeviceFunction
# ----------------------------------------------------------------------

class DeviceFunction(ABC):
    """
    Base class for a device function (command/response pair).
    """

    def __init__(
        self,
        request_length: int = 0,
        response_length: int = 0,
    ) -> None:
        self._request_length = request_length
        self._response_length = response_length

        self._request = Packet(self.code, request_length)
        self._response = Packet(self.code, response_length)

        # Measured externally by the dispatcher / transport layer
        self.transmission_time: int = 0

    # ------------------------------------------------------------------
    # Abstract API
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def code(self) -> int:
        """
        Function code (1 byte).
        """
        raise NotImplementedError

    @abstractmethod
    def create_dispatcher(self):
        """
        Create and return a dispatcher for this function.
        """
        raise NotImplementedError

    @abstractmethod
    def dispatch(self, listener: Any) -> int:
        """
        Dispatch this function to a listener.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Request / Response handling
    # ------------------------------------------------------------------

    def get_request(self, address: int) -> bytes:
        """
        Build and serialize the request packet for transmission.
        """
        pkt = self.get_request_packet()
        pkt.address = address
        return pkt.to_bytes()

    def get_response(self) -> bytes:
        """
        Serialize the response packet (used on the slave side).
        """
        return self.get_response_packet().to_bytes()

    def get_request_packet(self) -> Packet:
        """
        Override if request packet needs to be rebuilt dynamically.
        """
        return self._request

    def get_response_packet(self) -> Packet:
        """
        Override if response packet needs to be rebuilt dynamically.
        """
        return self._response

    def set_request(self, packet: Packet) -> DeviceFunction:
        """
        Set and validate a received request packet (slave side).
        """
        self._request = packet

        if packet.code != self.code:
            raise InvalidMasterRequestError(
                f"Invalid function code ({packet.code} != {self.code})"
            )

        if not self.is_request_valid():
            raise InvalidMasterRequestError(
                "Request is invalid (is_request_valid returned False)"
            )

        return self

    def set_response(self, packet: Packet) -> None:
        """
        Set and validate a received response packet (master side).
        """
        self._response = packet

        if packet.code != self._request.code:
            raise InvalidSlaveResponseError(
                f"Invalid function code ({packet.code} != {self._request.code})"
            )

        if not self.is_response_valid():
            raise InvalidSlaveResponseError(
                "Response is invalid (is_response_valid returned False)"
            )

    # ------------------------------------------------------------------
    # Validation hooks
    # ------------------------------------------------------------------

    def is_request_valid(self) -> bool:
        """
        Override if more than length validation is required.
        """
        return self._request.length == self._request_length

    def is_response_valid(self) -> bool:
        """
        Override if more than length validation is required.
        """
        return self._response.length == self._response_length

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_send(self) -> None:
        """
        Called just before the request is sent (master side).
        Override to populate the request packet.
        """
        pass

    def on_received(self) -> None:
        """
        Called after a response is received and validated (master side).
        Override to parse the response packet.
        """
        pass

    def on_slave_received(self) -> None:
        """
        Called when a request is received and validated (slave side).
        Override to parse the request packet.
        """
        pass

    def on_slave_send(self) -> None:
        """
        Called just before sending the response (slave side).
        Override to populate the response packet.
        """
        pass

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def address(self) -> int:
        """
        Address from the request packet, or -1 if not enabled.
        """
        return self._request.address if self._request.address_enabled else -1

    @property
    def request(self) -> Packet:
        return self._request
    
    def set_request(self, request) -> None:
        self._request = request

    @property
    def response(self) -> Packet:
        return self._response
