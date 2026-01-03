# labbench_comm/serial/base.py

from abc import ABC, abstractmethod
from typing import Tuple


class SerialIO(ABC):
    """
    Minimal byte-level serial I/O interface.

    This interface is intentionally small:
    - write_bytes() sends raw bytes
    - read_nonblocking() retrieves available bytes without blocking
    """

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @property
    @abstractmethod
    def is_open(self) -> bool:
        ...

    @abstractmethod
    def write_bytes(self, data: bytes) -> None:
        """
        Write raw bytes to the serial port.

        Must either write all bytes or raise.
        """
        ...

    @abstractmethod
    def read_nonblocking(self, max_bytes: int) -> Tuple[int, bytes]:
        """
        Read up to max_bytes without blocking.

        Returns (n_bytes, data).
        May return (0, b"") if no data is available.
        """
        ...
