from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .definitions import WaveformInstructionType


@dataclass
class WaveformInstruction:
    """
    Represents a single waveform instruction for the CPAR device.
    """

    operand: WaveformInstructionType = WaveformInstructionType.TRIG
    argument: float = 0.0
    time: float = 1.0

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def increment(cls, delta: float, time: float) -> "WaveformInstruction":
        return cls(
            operand=WaveformInstructionType.INC,
            argument=delta,
            time=time,
        )

    @classmethod
    def decrement(cls, delta: float, time: float) -> "WaveformInstruction":
        return cls(
            operand=WaveformInstructionType.DEC,
            argument=delta,
            time=time,
        )

    @classmethod
    def step(cls, pressure: float, time: float) -> "WaveformInstruction":
        return cls(
            operand=WaveformInstructionType.STEP,
            argument=pressure,
            time=time,
        )

    @classmethod
    def zero(cls) -> "WaveformInstruction":
        return cls(
            operand=WaveformInstructionType.STEP,
            argument=0.0,
            time=0.0,
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        if self.operand is WaveformInstructionType.INC:
            return (
                f"{self.operand.name} "
                f"({self.argument:0.3f} kPa/s, {self.time:0.2f} s)"
            )

        if self.operand is WaveformInstructionType.DEC:
            return (
                f"{self.operand.name} "
                f"(-{self.argument:0.3f} kPa/s, {self.time:0.2f} s)"
            )

        if self.operand is WaveformInstructionType.STEP:
            return (
                f"{self.operand.name} "
                f"({self.argument:0.3f} kPa, {self.time:0.2f} s)"
            )

        if self.operand is WaveformInstructionType.TRIG:
            return (
                f"{self.operand.name} "
                f"({self.argument:0.2f} s with offset {self.time:0.2f} s)"
            )

        return "WaveformInstruction"
