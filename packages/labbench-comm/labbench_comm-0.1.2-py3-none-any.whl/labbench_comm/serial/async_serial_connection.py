import asyncio
from typing import Optional

from labbench_comm.serial.base import SerialIO
from labbench_comm.protocols.destuffer import Destuffer


class AsyncSerialConnection:
    """
    Async transport wrapper around a non-blocking SerialIO.

    Responsibilities:
    - Manage serial port lifecycle
    - Run a background reader task
    - Feed raw bytes into a Destuffer
    - Provide async-safe write operations
    """

    def __init__(self, serial_io: SerialIO) -> None:
        self._io = serial_io
        self._destuffer: Optional[Destuffer] = None

        self._reader_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def attach_destuffer(self, destuffer: Destuffer) -> None:
        if destuffer is None:
            raise ValueError("destuffer must not be None")

        if self.is_open:
            raise RuntimeError("Cannot attach destuffer while connection is open")

        self._destuffer = destuffer

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        async with self._lock:
            if self.is_open:
                return

            if self._destuffer is None:
                raise RuntimeError("Destuffer must be attached before opening")

            self._io.open()

            self._reader_task = asyncio.create_task(
                self._reader_loop(),
                name="AsyncSerialConnection.reader",
            )

    async def close(self) -> None:
        async with self._lock:
            if not self.is_open:
                return

            if self._reader_task:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
                finally:
                    self._reader_task = None

            self._io.close()

    @property
    def is_open(self) -> bool:
        return self._io.is_open

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    async def write_bytes(self, data: bytes) -> None:
        if not self.is_open:
            raise RuntimeError("Connection is not open")

        # Offload blocking write
        await asyncio.to_thread(self._io.write_bytes, data)

    # ------------------------------------------------------------------
    # Background reader
    # ------------------------------------------------------------------

    async def _reader_loop(self) -> None:
        try:
            while True:
                n, data = self._io.read_nonblocking(1024)

                if n and self._destuffer:
                    self._destuffer.add_bytes(data)
                else:
                    # Avoid hot spinning when no data is available
                    await asyncio.sleep(0.001)

        except asyncio.CancelledError:
            # Normal shutdown path
            pass

        except Exception:
            # Any unexpected error should close the connection
            try:
                self._io.close()
            finally:
                raise

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
