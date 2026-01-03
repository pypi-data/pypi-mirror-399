from enum import IntEnum


class ErrorCode(IntEnum):
    """
    Protocol error codes.
    """

    NO_ERROR = 0x00
    UNKNOWN_FUNCTION_ERR = 0x01
    INVALID_CONTENT_ERR = 0x02
    DISPATCH_ERR = 0xFF
