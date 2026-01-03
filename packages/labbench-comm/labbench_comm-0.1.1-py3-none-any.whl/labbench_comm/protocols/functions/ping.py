from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher


class Ping(DeviceFunction):
    """
    Simple ping function used to verify connectivity and responsiveness.
    """

    @property
    def code(self) -> int:
        return 0x02

    def __init__(self) -> None:
        super().__init__(request_length=0, response_length=4)

    # ------------------------------------------------------------------
    # Dispatching
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: Ping())

    def dispatch(self, listener) -> int:
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Response fields
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        return self.response.get_uint32(0)

    @count.setter
    def count(self, value: int) -> None:
        self.response.insert_uint32(0, value)

    def __str__(self) -> str:
        return "[0x02] Ping"
