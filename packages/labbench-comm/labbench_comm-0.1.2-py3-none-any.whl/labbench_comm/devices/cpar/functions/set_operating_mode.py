from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher
from labbench_comm.devices.cpar.definitions import OperatingMode


class SetOperatingMode(DeviceFunction):
    @property
    def code(self) -> int:
        return 0x20

    def __init__(self) -> None:
        super().__init__(request_length=1, response_length=0)
        self.mode = OperatingMode.RESPONSE_ENABLED

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: SetOperatingMode())

    def dispatch(self, listener):
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def mode(self) -> OperatingMode:
        return OperatingMode(self.request.get_byte(0))

    @mode.setter
    def mode(self, value: OperatingMode) -> None:
        self.request.insert_byte(0, int(value))

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "[0x20] Set Operating Mode"
