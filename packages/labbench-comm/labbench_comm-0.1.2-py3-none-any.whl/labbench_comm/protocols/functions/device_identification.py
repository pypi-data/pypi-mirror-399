from labbench_comm.protocols.device_function import DeviceFunction
from labbench_comm.protocols.function_dispatcher import FunctionDispatcher
from labbench_comm.protocols.manufacturer import Manufacturer


class DeviceIdentification(DeviceFunction):
    """
    Standard device identification function.

    This function is expected to be implemented by all devices.
    """

    @property
    def code(self) -> int:
        return 0x01

    def __init__(self) -> None:
        super().__init__(request_length=0, response_length=64)

    # ------------------------------------------------------------------
    # Dispatching
    # ------------------------------------------------------------------

    def create_dispatcher(self) -> FunctionDispatcher:
        return FunctionDispatcher(self.code, lambda: DeviceIdentification())

    def dispatch(self, listener) -> int:
        return listener.accept(self)

    # ------------------------------------------------------------------
    # Response fields
    # ------------------------------------------------------------------

    @property
    def manufacturer_id(self) -> Manufacturer:
        return Manufacturer(self.response.get_uint32(0))

    @manufacturer_id.setter
    def manufacturer_id(self, value: Manufacturer) -> None:
        self.response.insert_uint32(0, int(value))

    @property
    def manufacturer(self) -> str:
        return self.response.get_string(16, 24)

    @manufacturer.setter
    def manufacturer(self, value: str) -> None:
        self.response.insert_string(16, 24, value)

    @property
    def device_id(self) -> int:
        return self.response.get_uint16(4)

    @device_id.setter
    def device_id(self, value: int) -> None:
        self.response.insert_uint16(4, value)

    @property
    def device(self) -> str:
        return self.response.get_string(40, 24)

    @device.setter
    def device(self, value: str) -> None:
        self.response.insert_string(40, 24, value)

    @property
    def major_version(self) -> int:
        return self.response.get_byte(10)

    @major_version.setter
    def major_version(self, value: int) -> None:
        self.response.insert_byte(10, value)

    @property
    def minor_version(self) -> int:
        return self.response.get_byte(11)

    @minor_version.setter
    def minor_version(self, value: int) -> None:
        self.response.insert_byte(11, value)

    @property
    def patch_version(self) -> int:
        return self.response.get_byte(12)

    @patch_version.setter
    def patch_version(self, value: int) -> None:
        self.response.insert_byte(12, value)

    @property
    def engineering_version(self) -> int:
        return self.response.get_byte(13)

    @engineering_version.setter
    def engineering_version(self, value: int) -> None:
        self.response.insert_byte(13, value)

    @property
    def version(self) -> str:
        if self.engineering_version == 0:
            return f"{self.major_version}.{self.minor_version}.{self.patch_version}"
        return (
            f"{self.major_version}."
            f"{self.minor_version}."
            f"{self.patch_version}.r{self.engineering_version}"
        )

    @property
    def serial_number(self) -> int:
        return self.response.get_uint32(6)

    @serial_number.setter
    def serial_number(self, value: int) -> None:
        self.response.insert_uint32(6, value)

    @property
    def checksum(self) -> int:
        return self.response.get_uint16(14)

    @checksum.setter
    def checksum(self, value: int) -> None:
        self.response.insert_uint16(14, value)

    def __str__(self) -> str:
        return "[0x01] Device Identification"
