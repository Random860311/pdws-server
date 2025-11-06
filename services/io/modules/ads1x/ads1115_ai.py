import traceback
from typing import Optional

import board
from adafruit_mcp3xxx.analog_in import AnalogIn

from services.io.modules.ai_module_protocol import AIModuleProtocol
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

class Ads1115_AI(AIModuleProtocol):
    def __init__(self):
        self.__channels: dict[int, AnalogIn] = {}
        try:
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
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()

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