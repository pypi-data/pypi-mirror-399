"""
Core LabBench protocol primitives.

This package contains:
- Framing and destuffing
- Packet encoding/decoding
- Device functions and messages
- Dispatch helpers
- Protocol-level exceptions and error codes
"""

# ----------------------------------------------------------------------
# Framing / transport helpers
# ----------------------------------------------------------------------

from .frame import Frame
from .destuffer import Destuffer

# ----------------------------------------------------------------------
# Packet
# ----------------------------------------------------------------------

from .packet import (
    Packet,
    LengthEncodingType,
    ChecksumAlgorithmType,
)

# ----------------------------------------------------------------------
# Base protocol types
# ----------------------------------------------------------------------

from .device_function import DeviceFunction
from .device_message import DeviceMessage

# ----------------------------------------------------------------------
# Dispatchers
# ----------------------------------------------------------------------

from .function_dispatcher import FunctionDispatcher
from .message_dispatcher import MessageDispatcher

# ----------------------------------------------------------------------
# Errors / exceptions
# ----------------------------------------------------------------------

from .exceptions import (
    PacketFormatError,
    InvalidMessageError,
    InvalidMasterRequestError,
    InvalidSlaveResponseError,
    PeripheralNotRespondingError,
    FunctionNotAcknowledgedError,
    IncompatibleDeviceError,
)

# ----------------------------------------------------------------------
# Error codes
# ----------------------------------------------------------------------

from .error_codes import ErrorCode

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

__all__ = [
    # Framing
    "Frame",
    "Destuffer",

    # Packet
    "Packet",
    "LengthEncodingType",
    "ChecksumAlgorithmType",

    # Base types
    "DeviceFunction",
    "DeviceMessage",

    # Dispatchers
    "FunctionDispatcher",
    "MessageDispatcher",

    # Errors
    "PacketFormatError",
    "InvalidMessageError",
    "InvalidMasterRequestError",
    "InvalidSlaveResponseError",
    "PeripheralNotRespondingError",
    "FunctionNotAcknowledgedError",
    "IncompatibleDeviceError",

    # Error codes
    "ErrorCode",
]
