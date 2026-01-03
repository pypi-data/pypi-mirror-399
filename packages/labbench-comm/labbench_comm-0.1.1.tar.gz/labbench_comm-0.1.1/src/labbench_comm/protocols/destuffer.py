from __future__ import annotations

from enum import Enum, auto
from typing import Callable, List, Optional
import logging

class Frame:
    """
    Framing constants.
    Adjust values if needed to match LabBench framing.
    """
    DLE = 0xFF
    STX = 0xF1
    ETX = 0xF2


class _State(Enum):
    WAITING_FOR_DLE = auto()
    WAITING_FOR_STX = auto()
    RECEIVING_DATA = auto()
    WAITING_FOR_ETX = auto()


class Destuffer:
    """
    Byte-stream destuffer implementing DLE/STX/ETX framing.

    Feed bytes incrementally using add_byte() or add_bytes().
    When a full frame is received, registered callbacks are invoked.
    """

    def __init__(self) -> None:
        self._state: _State = _State.WAITING_FOR_DLE
        self._buffer = bytearray()
        self._raw = bytearray()  # kept for parity with C# (future use)
        self._callbacks: List[Callable[[Destuffer, bytes], None]] = []
        self.log = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the state machine and discard buffered data."""
        self._state = _State.WAITING_FOR_DLE
        self._discard()

    def on_receive(self, callback: Callable[[Destuffer, bytes], None]) -> None:
        """
        Register a callback invoked when a full frame is received.
        """
        self._callbacks.append(callback)

    def add_bytes(self, data: bytes) -> None:
        """Add a sequence of bytes to the destuffer."""
        for b in data:
            self.add_byte(b)

    def add_byte(self, data: int) -> None:
        """Add a single byte (0–255)."""

        if self._state is _State.WAITING_FOR_DLE:
            self._handle_waiting_for_dle(data)

        elif self._state is _State.WAITING_FOR_STX:
            self._handle_waiting_for_stx(data)

        elif self._state is _State.RECEIVING_DATA:
            self._handle_receiving_data(data)

        elif self._state is _State.WAITING_FOR_ETX:
            self._handle_waiting_for_etx(data)

    # ------------------------------------------------------------------
    # State handlers (direct port of C# logic)
    # ------------------------------------------------------------------

    def _handle_waiting_for_dle(self, data: int) -> None:
        if data == Frame.DLE:
            self._buffer.clear()
            self._state = _State.WAITING_FOR_STX

    def _handle_waiting_for_stx(self, data: int) -> None:
        if data == Frame.STX:
            self._state = _State.RECEIVING_DATA
            self._buffer.clear()
        elif data != Frame.DLE:
            self._state = _State.WAITING_FOR_DLE
            self._discard()

    def _handle_receiving_data(self, data: int) -> None:
        if data != Frame.DLE:
            self._buffer.append(data)
        else:
            self._state = _State.WAITING_FOR_ETX

    def _handle_waiting_for_etx(self, data: int) -> None:
        if data == Frame.DLE:
            # Escaped DLE
            self._buffer.append(Frame.DLE)
            self._state = _State.RECEIVING_DATA

        elif data == Frame.ETX:
            # End of frame
            self._state = _State.WAITING_FOR_DLE
            self._notify_listeners()
            self._discard()

        elif data == Frame.STX:
            # Restart frame
            self._state = _State.RECEIVING_DATA
            self._discard()

        else:
            # Invalid sequence
            self._state = _State.WAITING_FOR_DLE
            self._discard()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _discard(self) -> None:
        self._buffer.clear()
        self._raw.clear()

    def _notify_listeners(self) -> None:
        payload = bytes(self._buffer)
        for cb in self._callbacks:
            cb(self, payload)
