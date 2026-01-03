from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher

from labbench_comm.devices.cpar.definitions import (
    StopCriterion,
    DeviceChannelID,
)


class StartStimulation(DeviceFunction):
    @property
    def code(self) -> int:
        return 0x11

    def __init__(self) -> None:
        super().__init__(request_length=5, response_length=0)

        # Defaults (match firmware expectations)
        self.criterion = StopCriterion.STOP_CRITERION_ON_BUTTON_VAS
        self.outlet01 = DeviceChannelID.NONE
        self.outlet02 = DeviceChannelID.NONE
        self.override_rating = False
        self.external_trigger = False

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: StartStimulation())

    def dispatch(self, listener):
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Request fields
    # ------------------------------------------------------------------

    @property
    def criterion(self) -> StopCriterion:
        return StopCriterion(self.request.get_byte(0))

    @criterion.setter
    def criterion(self, value: StopCriterion) -> None:
        self.request.insert_byte(0, int(value))

    @property
    def outlet01(self) -> DeviceChannelID:
        return DeviceChannelID(self.request.get_byte(1))

    @outlet01.setter
    def outlet01(self, value: DeviceChannelID) -> None:
        self.request.insert_byte(1, int(value))

    @property
    def outlet02(self) -> DeviceChannelID:
        return DeviceChannelID(self.request.get_byte(2))

    @outlet02.setter
    def outlet02(self, value: DeviceChannelID) -> None:
        self.request.insert_byte(2, int(value))

    @property
    def override_rating(self) -> bool:
        return self.request.get_bool(3)

    @override_rating.setter
    def override_rating(self, value: bool) -> None:
        self.request.insert_bool(3, value)

    @property
    def external_trigger(self) -> bool:
        return self.request.get_bool(4)

    @external_trigger.setter
    def external_trigger(self, value: bool) -> None:
        self.request.insert_bool(4, value)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "[0x11] Start Stimulation"
