from __future__ import annotations

from typing import Final

from .definitions import WaveformInstructionType
from .waveform import WaveformInstruction


class InstructionCodec:
    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    INSTRUCTIONS_LENGTH: Final[int] = 6

    UPDATE_RATE: Final[float] = 100.0
    MAX_PRESSURE: Final[float] = 100.0
    MAX_TIME: Final[float] = 60.0 * 10.0  # seconds

    _MAX_OPERAND_VALUE: Final[int] = 0x3FFFFFFF
    _OPCODE_MASK: Final[int] = 0xC00000000000
    _OPERAND_MASK: Final[int] = 0x3FFFFFFF0000
    _CYCLE_MASK: Final[int] = 0x00000000FFFF

    # ------------------------------------------------------------------
    # Encoding helpers
    # ------------------------------------------------------------------

    @classmethod
    def argument_encoding(
        cls,
        operand: WaveformInstructionType,
        argument: float,
    ) -> int:
        if operand in (WaveformInstructionType.INC, WaveformInstructionType.DEC):
            return cls._pressure_to_binary(argument / cls.UPDATE_RATE)
        if operand is WaveformInstructionType.STEP:
            return cls._pressure_to_binary(argument)
        if operand is WaveformInstructionType.TRIG:
            return cls._time_to_binary(argument)
        return 0

    @classmethod
    def time_encoding(cls, time: float) -> int:
        return cls._time_to_binary(time)

    @classmethod
    def _pressure_to_binary(cls, pressure: float) -> int:
        pressure = max(0.0, min(pressure, cls.MAX_PRESSURE))
        scale = pressure / cls.MAX_PRESSURE
        return int(scale * cls._MAX_OPERAND_VALUE)

    @classmethod
    def _binary_to_pressure(cls, binary: int) -> float:
        scale = binary / cls._MAX_OPERAND_VALUE
        pressure = cls.MAX_PRESSURE * scale
        return min(pressure, cls.MAX_PRESSURE)

    @classmethod
    def _binary_to_time(cls, binary: int) -> float:
        time = binary / cls.UPDATE_RATE
        return min(time, cls.MAX_TIME)

    @classmethod
    def _time_to_binary(cls, time: float) -> int:
        if time < 0:
            time = 0.0
        if time > cls.MAX_TIME:
            raise ValueError(
                f"Instruction exceeds maximal duration of {cls.MAX_TIME} seconds"
            )
        return int(cls.UPDATE_RATE * time)

    # ------------------------------------------------------------------
    # Public encode / decode
    # ------------------------------------------------------------------

    @classmethod
    def encode(cls, instruction: WaveformInstruction) -> bytes:
        opcode = int(instruction.operand)
        data = opcode << 46

        if instruction.operand is WaveformInstructionType.STEP:
            if instruction.argument > cls.MAX_PRESSURE:
                raise ValueError(
                    f"STEP instruction pressure {instruction.argument} kPa "
                    f"exceeds maximum {cls.MAX_PRESSURE} kPa"
                )

            data |= cls._pressure_to_binary(instruction.argument) << 16
            data |= cls._time_to_binary(instruction.time)

        elif instruction.operand in (
            WaveformInstructionType.INC,
            WaveformInstructionType.DEC,
        ):
            data |= cls._pressure_to_binary(
                instruction.argument / cls.UPDATE_RATE
            ) << 16
            data |= cls._time_to_binary(instruction.time)

        elif instruction.operand is WaveformInstructionType.TRIG:
            data |= cls._time_to_binary(instruction.time)

        raw = data.to_bytes(8, byteorder="little", signed=False)
        return raw[: cls.INSTRUCTIONS_LENGTH]

    @classmethod
    def decode(cls, data: bytes) -> WaveformInstruction:
        if data is None:
            raise ValueError("data must not be None")

        if len(data) != cls.INSTRUCTIONS_LENGTH:
            raise ValueError(
                f"Decode expects {cls.INSTRUCTIONS_LENGTH} bytes"
            )

        padded = data + b"\x00" * (8 - cls.INSTRUCTIONS_LENGTH)
        binary = int.from_bytes(padded, byteorder="little", signed=False)

        operand = WaveformInstructionType(
            (binary & cls._OPCODE_MASK) >> 46
        )

        instr = WaveformInstruction(operand=operand)

        if operand is WaveformInstructionType.STEP:
            instr.argument = cls._binary_to_pressure(
                (binary & cls._OPERAND_MASK) >> 16
            )
            instr.time = cls._binary_to_time(binary & cls._CYCLE_MASK)

        elif operand in (
            WaveformInstructionType.INC,
            WaveformInstructionType.DEC,
        ):
            instr.argument = (
                cls._binary_to_pressure(
                    (binary & cls._OPERAND_MASK) >> 16
                )
                * cls.UPDATE_RATE
            )
            instr.time = cls._binary_to_time(binary & cls._CYCLE_MASK)

        elif operand is WaveformInstructionType.TRIG:
            instr.argument = cls._binary_to_time(
                (binary & cls._OPERAND_MASK) >> 16
            )
            instr.time = cls._binary_to_time(binary & cls._CYCLE_MASK)

        return instr
