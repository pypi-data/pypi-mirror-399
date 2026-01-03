from enum import Enum
from labbench_comm.devices.cpar.instruction_codec import InstructionCodec


class CPARplusCodec:
    class PressureType(Enum):
        SUPPLY_PRESSURE = 0
        STIMULATING_PRESSURE = 1

    MAX_SUPPLY_PRESSURE = 1000.0
    MAX_SCORE = 10.0

    @staticmethod
    def time_to_rate(time: float) -> int:
        return round(time * InstructionCodec.UPDATE_RATE)

    @staticmethod
    def binary_to_pressure(
        value: int,
        pressure_type: "CPARplusCodec.PressureType" = PressureType.STIMULATING_PRESSURE,
    ) -> float:
        if pressure_type is CPARplusCodec.PressureType.SUPPLY_PRESSURE:
            return CPARplusCodec.MAX_SUPPLY_PRESSURE * value / 4095
        return InstructionCodec.MAX_PRESSURE * value / 4095

    @staticmethod
    def binary_to_score(value: int) -> float:
        return CPARplusCodec.MAX_SCORE * value / 255

    @staticmethod
    def pressure_to_binary(pressure: float) -> int:
        return InstructionCodec._pressure_to_binary(pressure)

    @staticmethod
    def delta_pressure_to_binary(delta: float) -> int:
        return InstructionCodec._pressure_to_binary(
            delta / InstructionCodec.UPDATE_RATE
        )

    @staticmethod
    def count_to_time(count: int) -> float:
        return count / InstructionCodec.UPDATE_RATE

    @staticmethod
    def time_to_count(time: float) -> int:
        return int((time * InstructionCodec.UPDATE_RATE) + 0.9999)

    @staticmethod
    def get_time(samples: int) -> float:
        return CPARplusCodec.count_to_time(samples)
