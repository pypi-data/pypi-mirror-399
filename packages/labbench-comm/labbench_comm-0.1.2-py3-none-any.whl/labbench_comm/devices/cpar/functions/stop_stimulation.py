from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher


class StopStimulation(DeviceFunction):
    @property
    def code(self) -> int:
        return 0x13

    def __init__(self) -> None:
        super().__init__(request_length=0, response_length=0)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: StopStimulation())

    def dispatch(self, listener):
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "[0x13] Stop Stimulation"
