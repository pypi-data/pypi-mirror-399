from __future__ import annotations


def additive_checksum(data: bytes, length: int | None = None) -> int:
    """
    Compute an additive checksum over the given data.

    The checksum is the simple byte-wise sum modulo 256.
    """

    checksum = 0x00

    if data is None:
        return checksum

    if length is None:
        length = len(data)

    for i in range(length):
        checksum = (checksum + data[i]) & 0xFF

    return checksum
