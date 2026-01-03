from __future__ import annotations

from enum import IntEnum
from typing import Tuple
import struct

from labbench_comm.protocols.exceptions import ChecksumError, PacketFormatError
from labbench_comm.utils.additive_checksum import additive_checksum
from labbench_comm.utils.crc8_ccitt import crc8_ccitt


class LengthEncodingType(IntEnum):
    UINT8 = 0x00
    UINT16 = 0x01
    UINT32 = 0x02


class ChecksumAlgorithmType(IntEnum):
    NONE = 0x00
    ADDITIVE = 0x04
    CRC8CCITT = 0x08


class Packet:
    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        code: int,
        length: int,
        checksum: ChecksumAlgorithmType = ChecksumAlgorithmType.NONE,
    ) -> None:
        self._code = code & 0xFF
        self._length = length
        self._length_encoding = self._get_length_encoding(length)
        self._checksum_type = checksum

        self.address: int = 0
        self.reverse_endianity: bool = False

        self._checksum: int = 0
        self._data = bytearray(length)

    @classmethod
    def from_frame(cls, frame: bytes) -> Packet:
        if frame is None or len(frame) < 2:
            raise PacketFormatError("Frame too short")

        code = frame[0]
        fmt = frame[1]

        if fmt < 0x80:
            length = fmt
            pkt = cls(code, length)
            pkt._data[:] = frame[2 : 2 + length]
            return pkt

        length_encoding = LengthEncodingType(fmt & 0x03)
        checksum_type = ChecksumAlgorithmType(fmt & 0x0C)
        address_enabled = bool(fmt & 0x10)

        offset = 2
        length, offset = cls._decode_length(frame, length_encoding, offset)

        pkt = cls(code, length, checksum_type)
        pkt._length_encoding = length_encoding

        if address_enabled:
            pkt.address = frame[offset]
            offset += 1

        pkt._data[:] = frame[offset : offset + length]
        offset += length

        if checksum_type != ChecksumAlgorithmType.NONE:
            pkt._checksum = frame[offset]
            cls._validate_checksum(frame[:offset], pkt._checksum, checksum_type)

        return pkt

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def code(self) -> int:
        return self._code

    @property
    def is_function(self) -> bool:
        return self._code < 0x80

    @property
    def length(self) -> int:
        return self._length

    @property
    def empty(self) -> bool:
        return self._length == 0

    @property
    def address_enabled(self) -> bool:
        return self.address != 0

    @property
    def checksum(self) -> int:
        return self._checksum

    @property
    def checksum_algorithm(self) -> ChecksumAlgorithmType:
        return self._checksum_type

    @property
    def extended(self) -> bool:
        if self.address_enabled:
            return True
        if self.checksum_algorithm != ChecksumAlgorithmType.NONE:
            return True
        if self._length_encoding in (LengthEncodingType.UINT16, LengthEncodingType.UINT32):
            return True
        return self._length >= 128

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_bytes(self) -> bytes:
        if not self.extended:
            return bytes([self._code, self._length]) + bytes(self._data)

        header = bytearray()
        header.append(self._code)
        header.append(
            0x80
            | self._length_encoding
            | self._checksum_type
            | (0x10 if self.address_enabled else 0x00)
        )

        header.extend(self._encode_length())

        if self.address_enabled:
            header.append(self.address)

        payload = bytes(self._data)
        packet = header + payload

        if self._checksum_type == ChecksumAlgorithmType.ADDITIVE:
            self._checksum = additive_checksum(packet)
            packet += bytes([self._checksum])
        elif self._checksum_type == ChecksumAlgorithmType.CRC8CCITT:
            self._checksum = crc8_ccitt(packet)
            packet += bytes([self._checksum])

        return bytes(packet)

    # ------------------------------------------------------------------
    # Insert methods
    # ------------------------------------------------------------------

    def insert_byte(self, pos: int, value: int) -> None:
        self._data[pos] = value & 0xFF

    def insert_bool(self, pos: int, value: bool) -> None:
        self.insert_byte(pos, 1 if value else 0)

    def insert_uint16(self, pos: int, value: int) -> None:
        self._serialize(pos, struct.pack("<H", value))

    def insert_int16(self, pos: int, value: int) -> None:
        self._serialize(pos, struct.pack("<h", value))

    def insert_uint32(self, pos: int, value: int) -> None:
        self._serialize(pos, struct.pack("<I", value))

    def insert_int32(self, pos: int, value: int) -> None:
        self._serialize(pos, struct.pack("<i", value))

    def insert_string(self, pos: int, size: int, value: str) -> None:
        raw = value.encode("ascii", errors="ignore")[:size]
        self._data[pos : pos + size] = raw.ljust(size, b"\x00")

    # ------------------------------------------------------------------
    # Get methods
    # ------------------------------------------------------------------

    def get_byte(self, pos: int) -> int:
        return self._data[pos]

    def get_bool(self, pos: int) -> bool:
        return self.get_byte(pos) != 0

    def get_uint16(self, pos: int) -> int:
        return self._deserialize(pos, "<H")

    def get_int16(self, pos: int) -> int:
        return self._deserialize(pos, "<h")

    def get_uint32(self, pos: int) -> int:
        return self._deserialize(pos, "<I")

    def get_int32(self, pos: int) -> int:
        return self._deserialize(pos, "<i")

    def get_string(self, pos: int, size: int) -> str:
        raw = self._data[pos : pos + size]
        return raw.rstrip(b"\x00").decode("ascii", errors="ignore")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _serialize(self, pos: int, data: bytes) -> None:
        if self.reverse_endianity:
            data = data[::-1]
        self._data[pos : pos + len(data)] = data

    def _deserialize(self, pos: int, fmt: str) -> int:
        size = struct.calcsize(fmt)
        raw = self._data[pos : pos + size]
        if self.reverse_endianity:
            raw = raw[::-1]
        return struct.unpack(fmt, raw)[0]

    @staticmethod
    def _get_length_encoding(length: int) -> LengthEncodingType:
        if length > 0xFFFF:
            return LengthEncodingType.UINT32
        if length > 0xFF:
            return LengthEncodingType.UINT16
        return LengthEncodingType.UINT8

    def _encode_length(self) -> bytes:
        if self._length_encoding == LengthEncodingType.UINT8:
            return bytes([self._length])
        if self._length_encoding == LengthEncodingType.UINT16:
            return struct.pack("<H", self._length)
        return struct.pack("<I", self._length)

    @staticmethod
    def _decode_length(
        frame: bytes,
        encoding: LengthEncodingType,
        offset: int,
    ) -> Tuple[int, int]:
        if encoding == LengthEncodingType.UINT8:
            return frame[offset], offset + 1
        if encoding == LengthEncodingType.UINT16:
            return struct.unpack_from("<H", frame, offset)[0], offset + 2
        return struct.unpack_from("<I", frame, offset)[0], offset + 4

    @staticmethod
    def _validate_checksum(
        data: bytes,
        expected: int,
        algo: ChecksumAlgorithmType,
    ) -> None:
        if algo == ChecksumAlgorithmType.ADDITIVE:
            actual = additive_checksum(data)
        elif algo == ChecksumAlgorithmType.CRC8CCITT:
            actual = crc8_ccitt(data)
        else:
            return

        if actual != expected:
            raise ChecksumError(
                f"Checksum mismatch (expected {expected}, got {actual})"
            )
