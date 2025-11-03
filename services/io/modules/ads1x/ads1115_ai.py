from typing import Optional

import board
from adafruit_mcp3xxx.analog_in import AnalogIn

from services.io.modules.ai_module_protocol import AIModuleProtocol
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

class Ads1115_AI(AIModuleProtocol):
    def __init__(self):
        # # create the spi bus
        # self.__spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # # create the cs (chip select)
        # self.__cs = digitalio.DigitalInOut(board.D5)
        # # create the mcp object
        # self.__mcp = MCP.MCP3008(self.__spi, self.__cs)
        # # create an analog input channel on pin 0

        # Create the I2C bus
        i2c = board.I2C()

        # Create the ADC object using the I2C bus
        ads = ADS1115(i2c)

        self.__channels: dict[int, AnalogIn] = {
            0: AnalogIn(ads, ads1x15.Pin.A0),
            1: AnalogIn(ads, ads1x15.Pin.A1),
            2: AnalogIn(ads, ads1x15.Pin.A2),
            3: AnalogIn(ads, ads1x15.Pin.A3)
        }

    def get_value(self, ai_pos: int) -> Optional[int]:
        chan = self.__channels.get(ai_pos, None)
        if not chan:
            return None
        return chan.value

    def get_all_values(self) -> list[int]:
        return [chan.value for chan in self.__channels.values()]

    def get_max_value(self) -> int:
        # 24550~24729
        return 24729
        # return 65535

    @property
    def io_count(self) -> int:
        return 4