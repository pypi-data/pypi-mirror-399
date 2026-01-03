"""
CPAR+ device support.

This package provides:
- The CPARplusCentral device implementation
- CPAR-specific functions and messages
- Waveform and instruction utilities
- Device-specific enums and definitions
"""

# ----------------------------------------------------------------------
# Device
# ----------------------------------------------------------------------

from .cpar_central import CPARplusCentral

# ----------------------------------------------------------------------
# Definitions / enums
# ----------------------------------------------------------------------

from .definitions import (
    DeviceChannelID,
    DeviceState,
    EcpError,
    EventID,
    OperatingMode,
    StopCondition,
    StopCriterion,
    WaveformInstructionType,
)

# ----------------------------------------------------------------------
# Waveform
# ----------------------------------------------------------------------

from .waveform import WaveformInstruction
from .instruction_codec import InstructionCodec

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

from .functions import (
    SetWaveformProgram,
    StartStimulation,
    StopStimulation,
    SetOperatingMode,
    ClearWaveformPrograms,
)

# ----------------------------------------------------------------------
# Messages
# ----------------------------------------------------------------------

from .messages import (
    StatusMessage,
    EventMessage,
)

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

__all__ = [
    # Device
    "CPARplusCentral",

    # Enums / definitions
    "DeviceChannelID",
    "DeviceState",
    "EcpError",
    "EventID",
    "OperatingMode",
    "StopCondition",
    "StopCriterion",
    "WaveformInstructionType",

    # Waveform
    "WaveformInstruction",
    "InstructionCodec",

    # Functions
    "SetWaveformProgram",
    "StartStimulation",
    "StopStimulation",
    "SetOperatingMode",
    "ClearWaveformPrograms",

    # Messages
    "StatusMessage",
    "EventMessage",
]
