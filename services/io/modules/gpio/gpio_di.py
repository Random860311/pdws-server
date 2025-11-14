from typing import Optional
import pigpio

from services.io.modules.gpio.gpio_map import GPIO_DI_MAP
from services.io.modules.di_module_protocol import DIModuleProtocol
from services.io.modules.gpio.gpio_dio import GpioDio


class GPIO_DI(DIModuleProtocol, GpioDio):
    def __init__(self, pi: pigpio.pi):
        super().__init__(pi)

    @property
    def dio_map(self) -> dict[int, int]:
        return GPIO_DI_MAP

    def handle_pin_status(self, gpio: int, level: int, tick) -> None:
        print(f"GPIO {gpio} changed to {level}")
        if self.callback is None:
            return
        di_pos = self.dio_map.get(gpio, None)
        if di_pos is None:
            return
        self.callback(di_pos, level == 0)

    def get_all_values(self) -> list[bool]:
        result: list[bool] = []
        for gpio, di in self.dio_map.items():
            result.append(not bool(self.pi.read(gpio)))
        return result

    def get_value(self, dio_pos: int) -> Optional[bool]:
        for gpio, di in self.dio_map.items():
            if di == dio_pos:
                return not bool(self.pi.read(gpio))
        return None

    def initialize(self) -> None:
        for gpio_pin in self.dio_map.keys():
            self.pi.set_mode(gpio_pin, pigpio.INPUT)
            self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)

            self.add_gpio_callback(gpio_pin)




