# labbench_comm/serial/connection.py

from __future__ import annotations
from typing import Optional, Tuple

import serial
from serial import SerialException
import serial.tools.list_ports
import logging

from labbench_comm.serial.base import SerialIO
from labbench_comm.protocols.exceptions import (
    SerialError,
    SerialClosedError,
    SerialConnectionError,
)


class PySerialIO(SerialIO):
    """
    SerialIO implementation backed by pyserial.

    - Reads are strictly non-blocking (timeout=0)
    - Write errors and partial writes are detected
    - Safe under async cancellation and shutdown
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 38400,
        write_timeout: float = 1.0,
        *,
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: int = serial.STOPBITS_ONE,
        flush_on_write: bool = True,        
        dtr: bool = True,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._write_timeout = write_timeout

        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._flush_on_write = flush_on_write
        self._dtr = dtr

        self._serial: Optional[serial.Serial] = None
        self._log = logging.getLogger(__name__)

    # -------------------- Lifecycle -------------------- #

    def open(self) -> None:
        if self.is_open:
            return

        try:
            ser = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=0.0,  # strictly non-blocking
                write_timeout=self._write_timeout,
                bytesize=self._bytesize,
                parity=self._parity,
                stopbits=self._stopbits,
                dsrdtr=self._dtr
            )
        except SerialException as exc:
            raise SerialConnectionError(
                f"Failed to open serial port {self._port}"
            ) from exc

        if not ser.is_open:
            try:
                ser.close()
            finally:
                raise SerialConnectionError(
                    f"Serial port {self._port} did not open correctly"
                )

        # Explicit DTR control
        #try:
        #    ser.dtr = self._dtr
        #except SerialException as exc:
        #    ser.close()
        #    raise SerialConnectionError(
        #        "Failed to set DTR"
        #    ) from exc
            
        self._serial = ser

    def close(self) -> None:
        ser = self._serial
        self._serial = None

        if ser is not None:
            try:
                ser.close()
            except SerialException:
                pass

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def _require_open(self) -> serial.Serial:
        ser = self._serial
        if ser is None or not ser.is_open:
            raise SerialClosedError("Serial port is not open")
        return ser

    # -------------------- I/O -------------------- #

    def write_bytes(self, data: bytes) -> None:
        ser = self._require_open()

        try:
            written = ser.write(data)
            if self._flush_on_write:
                ser.flush()
        except SerialException as exc:
            raise SerialConnectionError("Serial write failed") from exc

        if written != len(data):
            raise SerialError(
                f"Partial write ({written}/{len(data)} bytes)"
            )

    def read_nonblocking(self, max_bytes: int) -> Tuple[int, bytes]:
        ser = self._serial
        if ser is None or not ser.is_open:
            return 0, b""

        try:
            available = ser.in_waiting
        except SerialException:
            return 0, b""

        if available <= 0:
            return 0, b""

        to_read = min(available, max_bytes)

        try:
            data = ser.read(to_read)
        except SerialException as exc:
            raise SerialConnectionError("Non-blocking read failed") from exc

        return len(data), data

    # -------------------- Utilities -------------------- #

    @staticmethod
    def list_ports() -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def __repr__(self) -> str:
        state = "open" if self.is_open else "closed"
        return (
            f"<PySerialIO port={self._port!r} "
            f"baudrate={self._baudrate} state={state}>"
        )
