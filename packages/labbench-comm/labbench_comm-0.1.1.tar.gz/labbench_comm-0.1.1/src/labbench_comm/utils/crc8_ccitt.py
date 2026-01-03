from __future__ import annotations


def crc8_ccitt(data: bytes, length: int | None = None) -> int:
    """
    Compute CRC-8-CCITT checksum.

    Polynomial: 0x07
    Initial value: 0x00
    """

    crc = 0x00

    if data is None:
        return crc

    if length is None:
        length = len(data)

    for i in range(length):
        crc = _update_crc8_ccitt(crc, data[i])

    return crc & 0xFF


def _update_crc8_ccitt(crc: int, value: int) -> int:
    """
    Update CRC with one byte.
    """
    data = (crc ^ value) & 0xFF

    for _ in range(8):
        if data & 0x80:
            data = ((data << 1) ^ 0x07) & 0xFF
        else:
            data = (data << 1) & 0xFF

    return data
