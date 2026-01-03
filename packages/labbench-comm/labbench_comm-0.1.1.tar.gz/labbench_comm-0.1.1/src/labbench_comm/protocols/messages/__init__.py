"""
Protocol-level device messages.

This package contains generic LabBench protocol messages that are
independent of any specific device implementation.
"""

# ----------------------------------------------------------------------
# Common / core messages
# ----------------------------------------------------------------------

from .printf_message import PrintfMessage

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

__all__ = [
    "PrintfMessage",
]
