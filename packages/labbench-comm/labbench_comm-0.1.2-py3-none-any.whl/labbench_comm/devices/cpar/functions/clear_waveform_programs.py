from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher


class ClearWaveformPrograms(DeviceFunction):
    @property
    def code(self) -> int:
        return 0x21

    def __init__(self) -> None:
        super().__init__(request_length=0, response_length=0)

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: ClearWaveformPrograms())

    def dispatch(self, listener):
        return listener.accept(self)

    def __str__(self) -> str:
        return "[0x21] Clear Waveform Programs"
