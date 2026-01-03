from typing import List

from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher
from labbench_comm.protocols.packet import Packet
from labbench_comm.utils.crc8_ccitt import crc8_ccitt

from labbench_comm.devices.cpar.waveform import WaveformInstruction
from labbench_comm.devices.cpar.instruction_codec import InstructionCodec


class SetWaveformProgram(DeviceFunction):
    MAX_NO_OF_INSTRUCTIONS = 256

    @property
    def code(self) -> int:
        return 0x10

    def __init__(self) -> None:
        super().__init__(request_length=0, response_length=1)
        self.instructions: List[WaveformInstruction] = []
        self._channel: int = 0
        self._repeat: int = 1

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: SetWaveformProgram())

    def dispatch(self, listener):
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def is_request_valid(self) -> bool:
        return True

    def is_response_valid(self) -> bool:
        return self.actual_checksum == self.expected_checksum

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def channel(self) -> int:
        return self._channel

    @channel.setter
    def channel(self, value: int) -> None:
        self._channel = 0 if value < 0 else 1 if value > 1 else value

    @property
    def repeat(self) -> int:
        return self._repeat

    @repeat.setter
    def repeat(self, value: int) -> None:
        self._repeat = value if value > 0 else 1

    @property
    def number_of_instructions(self) -> int:
        return min(len(self.instructions), self.MAX_NO_OF_INSTRUCTIONS)

    @property
    def expected_checksum(self) -> int:
        return crc8_ccitt(self.serialize_instructions())

    @property
    def actual_checksum(self) -> int:
        return self.response.get_byte(0) if self.response else 0

    @actual_checksum.setter
    def actual_checksum(self, value: int) -> None:
        self.response.insert_byte(0, value)

    @property
    def program_length(self) -> float:
        length = 0.0
        for instr in self.instructions:
            if instr.operand.name != "TRIG":
                length += instr.time
        return self.repeat * length

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def serialize_instructions(self) -> bytes:
        encoded = bytearray()
        for instr in self.instructions[: self.number_of_instructions]:
            encoded.extend(InstructionCodec.encode(instr))
        return bytes(encoded)

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_send(self) -> None:
        encoded = self.serialize_instructions()

        self.set_request(Packet(
            self.code,
            length=len(encoded) + 2,
        ))

        self.request.insert_byte(0, self.channel)
        self.request.insert_byte(1, self.repeat)

        for i, b in enumerate(encoded):
            self.request.insert_byte(i + 2, b)

    def on_slave_received(self) -> None:
        if self.request is None:
            return

        self.channel = self.request.get_byte(0)
        self.repeat = self.request.get_byte(1)

        self.instructions.clear()

        offset = 2
        count = (self.request.length - 2) // InstructionCodec.INSTRUCTIONS_LENGTH

        for _ in range(count):
            chunk = bytes(
                self.request.get_byte(offset + i)
                for i in range(InstructionCodec.INSTRUCTIONS_LENGTH)
            )
            self.instructions.append(InstructionCodec.decode(chunk))
            offset += InstructionCodec.INSTRUCTIONS_LENGTH

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return "[0x10] Set Waveform Program"
