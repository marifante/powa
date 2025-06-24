import struct
from smbus2 import SMBus


_REGISTERS = {
    "VOLTAGE" : 0x02,
    "CURRENT" : 0x01,
    "POWER"   : 0x03,
    "MANUFACTURER_ID" : 0xFE,
    "DIE_ID" : 0xFF
}


class Ina260:

    def __init__(self, address : int = 0x40, channel : int = 1):
        self.i2c_channel = channel
        self.bus = SMBus(self.i2c_channel)
        self.address = address

    def _read(self, reg: int) -> bytearray:
        """ Read a word from the device

        :param reg: register address
        :return: list of bytes as characters for struct unpack
        """
        res = self.bus.read_i2c_block_data(self.address, reg, 2)
        return bytearray(res)

    @property
    def voltage(self) -> float:
        """ Returns the bus voltage in Volts """
        voltage = struct.unpack('>H', self._read(_REGISTERS['VOLTAGE']))[0]
        voltage *= 0.00125 # 1.25mv/bit

        return voltage

    @property
    def current(self) -> float:
        """ Returns the current in Amps. """
        current = struct.unpack('>H', self._read(_REGISTERS['CURRENT']))[0]

        # Fix 2's complement
        if current & (1 << 15):
            current -= 65535

        current *= 0.00125 # 1.25mA/bit

        return current

    @property
    def power(self) -> float:
        """ Returns the power calculated by the device in Watts

        This will probably be different to reading voltage and current
        and performing the calculation manually.
        """
        power = struct.unpack('>H', self._read(_REGISTERS['POWER']))[0]
        power *= 0.01 # 10mW/bit

        return power

    def manufacturer_id(self):
        """
        Returns the manufacturer ID - should always be 0x5449

        """
        man_id = struct.unpack('>H', self._read(_REGISTERS["MANUFACTURER_ID"]))[0]
        return man_id


    def die_id(self):
        """
        Returns a tuple containing the die ID and revision - should be 0x227 and 0x0.
        """
        die_id = struct.unpack('>H', self._read(_REGISTERS["DIE_ID"]))[0]
        return (die_id >> 4), (die_id & 0x000F)

    def __del__(self):
        self.bus.close()
