from abc import ABC, abstractmethod
from typing import Callable


class AsyncConnection(ABC):

    @abstractmethod
    async def open(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @property
    @abstractmethod
    def is_open(self) -> bool:
        ...

    @abstractmethod
    async def write_bytes(self, data: bytes) -> None:
        ...

    @abstractmethod
    def attach_destuffer(self, destuffer) -> None:
        """
        Called once to attach the Destuffer.
        Incoming bytes MUST be forwarded to it.
        """
