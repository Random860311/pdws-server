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

    def initialize(self) -> None:
        for gpio_pin in self.dio_map.keys():
            self.pi.set_mode(gpio_pin, pigpio.INPUT)
            self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)

            self.add_gpio_callback(gpio_pin)




