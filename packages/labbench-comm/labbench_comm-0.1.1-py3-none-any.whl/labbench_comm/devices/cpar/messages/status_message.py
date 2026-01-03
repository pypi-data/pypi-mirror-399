from labbench_comm.protocols.device_message import DeviceMessage
from labbench_comm.protocols.message_dispatcher import MessageDispatcher
from labbench_comm.protocols.packet import Packet
from labbench_comm.protocols.exceptions import InvalidMessageError

from labbench_comm.devices.cpar.definitions import (
    DeviceState,
    StopCondition,
)

from labbench_comm.devices.cpar.codec import CPARplusCodec


class StatusMessage(DeviceMessage):
    @property
    def code(self) -> int:
        return 0x80

    def __init__(self, response: Packet | None = None) -> None:
        if response is not None:
            super().__init__(response)
            if self.packet.length != 22:
                raise InvalidMessageError(
                    "A received StatusMessage does not have a length of 22"
                )
        else:
            super().__init__(length=22)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> MessageDispatcher:
        return MessageDispatcher(self.code, lambda p: StatusMessage(p))

    def dispatch(self, listener) -> None:
        if hasattr(listener, "on_status_message"):
            listener.on_status_message(self)

    # ------------------------------------------------------------------
    # 1. System State
    # ------------------------------------------------------------------

    @property
    def system_state(self) -> DeviceState:
        return DeviceState(self.packet.get_byte(0) + 1)

    @property
    def system_state_binary(self) -> int:
        return self.packet.get_byte(0)

    @system_state_binary.setter
    def system_state_binary(self, value: int) -> None:
        self.packet.insert_byte(0, value)

    # ------------------------------------------------------------------
    # 2. System Status Flags (byte 1)
    # ------------------------------------------------------------------

    @property
    def vas_connected(self) -> bool:
        return (self.packet.get_byte(1) & 0x01) != 0

    @property
    def vas_is_low(self) -> bool:
        return (self.packet.get_byte(1) & 0x02) != 0

    @property
    def power_on(self) -> bool:
        return (self.packet.get_byte(1) & 0x04) != 0

    @property
    def compressor_running(self) -> bool:
        return (self.packet.get_byte(1) & 0x08) != 0

    @property
    def start_possible(self) -> bool:
        return (self.packet.get_byte(1) & 0x10) != 0

    @property
    def supply_pressure_low(self) -> bool:
        return (self.packet.get_byte(1) & 0x20) != 0

    @property
    def system_status_binary(self) -> int:
        return self.packet.get_byte(1)

    @system_status_binary.setter
    def system_status_binary(self, value: int) -> None:
        self.packet.insert_byte(1, value)

    # ------------------------------------------------------------------
    # 3. Waveform Program
    # ------------------------------------------------------------------

    @property
    def update_counter(self) -> int:
        return self.packet.get_uint16(2)

    @update_counter.setter
    def update_counter(self, value: int) -> None:
        self.packet.insert_uint16(2, value)

    @property
    def stop_condition(self) -> StopCondition:
        return StopCondition(self.packet.get_byte(4))

    @stop_condition.setter
    def stop_condition(self, value: StopCondition) -> None:
        self.packet.insert_byte(4, int(value))

    # ------------------------------------------------------------------
    # 4. Pain Rating
    # ------------------------------------------------------------------

    @property
    def vas_score(self) -> float:
        return CPARplusCodec.binary_to_score(self.packet.get_byte(5))

    @property
    def vas_score_binary(self) -> int:
        return self.packet.get_byte(5)

    @vas_score_binary.setter
    def vas_score_binary(self, value: int) -> None:
        self.packet.insert_byte(5, value)

    @property
    def final_vas_score(self) -> float:
        return CPARplusCodec.binary_to_score(self.packet.get_byte(6))

    @property
    def final_vas_score_binary(self) -> int:
        return self.packet.get_byte(6)

    @final_vas_score_binary.setter
    def final_vas_score_binary(self, value: int) -> None:
        self.packet.insert_byte(6, value)

    # ------------------------------------------------------------------
    # 5. Supply Pressure
    # ------------------------------------------------------------------

    @property
    def supply_pressure(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.supply_pressure_binary,
            CPARplusCodec.PressureType.SUPPLY_PRESSURE,
        )

    @property
    def supply_pressure_binary(self) -> int:
        return self.packet.get_uint16(7)

    @supply_pressure_binary.setter
    def supply_pressure_binary(self, value: int) -> None:
        self.packet.insert_uint16(7, value)

    # ------------------------------------------------------------------
    # 6. Stimulation Pressures
    # ------------------------------------------------------------------

    @property
    def actual_pressure_01(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.actual_pressure_01_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def actual_pressure_01_binary(self) -> int:
        return self.packet.get_uint16(9)

    @actual_pressure_01_binary.setter
    def actual_pressure_01_binary(self, value: int) -> None:
        self.packet.insert_uint16(9, value)

    @property
    def actual_pressure_02(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.actual_pressure_02_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def actual_pressure_02_binary(self) -> int:
        return self.packet.get_uint16(11)

    @actual_pressure_02_binary.setter
    def actual_pressure_02_binary(self, value: int) -> None:
        self.packet.insert_uint16(11, value)

    @property
    def target_pressure_01(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.target_pressure_01_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def target_pressure_01_binary(self) -> int:
        return self.packet.get_uint16(13)

    @target_pressure_01_binary.setter
    def target_pressure_01_binary(self, value: int) -> None:
        self.packet.insert_uint16(13, value)

    @property
    def target_pressure_02(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.target_pressure_02_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def target_pressure_02_binary(self) -> int:
        return self.packet.get_uint16(15)

    @target_pressure_02_binary.setter
    def target_pressure_02_binary(self, value: int) -> None:
        self.packet.insert_uint16(15, value)

    @property
    def final_pressure_01(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.final_pressure_01_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def final_pressure_01_binary(self) -> int:
        return self.packet.get_uint16(17)

    @final_pressure_01_binary.setter
    def final_pressure_01_binary(self, value: int) -> None:
        self.packet.insert_uint16(17, value)

    @property
    def final_pressure_02(self) -> float:
        return CPARplusCodec.binary_to_pressure(
            self.final_pressure_02_binary,
            CPARplusCodec.PressureType.STIMULATING_PRESSURE,
        )

    @property
    def final_pressure_02_binary(self) -> int:
        return self.packet.get_uint16(19)

    @final_pressure_02_binary.setter
    def final_pressure_02_binary(self, value: int) -> None:
        self.packet.insert_uint16(19, value)

    # ------------------------------------------------------------------
    # Stop button
    # ------------------------------------------------------------------

    @property
    def stop_pressed(self) -> bool:
        return self.packet.get_byte(21) != 0

    @stop_pressed.setter
    def stop_pressed(self, value: bool) -> None:
        self.packet.insert_byte(21, 1 if value else 0)
