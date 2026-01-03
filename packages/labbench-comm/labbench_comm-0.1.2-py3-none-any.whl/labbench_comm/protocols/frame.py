from __future__ import annotations


class Frame:
    """
    DLE/STX/ETX framing and byte-stuffing utilities.

    This class is the inverse of Destuffer.
    """

    # Framing constants (ported exactly)
    DLE: int = 0xFF
    STX: int = 0xF1
    ETX: int = 0xF2

    @staticmethod
    def encode(packet: bytes) -> bytes:
        """
        Encode a payload into a framed, DLE-stuffed byte sequence.

        Equivalent to LabBench.IO.Frame.Encode in C#.
        """
        if packet is None:
            raise ValueError("packet must not be None")

        buffer = bytearray()

        # Start of text
        buffer.append(Frame.DLE)
        buffer.append(Frame.STX)

        # Data with DLE stuffing
        for b in packet:
            if b == Frame.DLE:
                buffer.append(Frame.DLE)
                buffer.append(Frame.DLE)
            else:
                buffer.append(b)

        # End of text
        buffer.append(Frame.DLE)
        buffer.append(Frame.ETX)

        return bytes(buffer)
