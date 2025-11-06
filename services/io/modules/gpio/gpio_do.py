from typing import Optional

import pigpio

from services.io.gpio_map import GPIO_DO_MAP
from services.io.modules.do_module_protocol import DOModuleProtocol
from services.io.modules.gpio.gpio_dio import GpioDio


class GPIO_DI(DOModuleProtocol, GpioDio):
    def __init__(self, pi: pigpio.pi):
        super().__init__(pi)

        for gpio_pin in GPIO_DO_MAP.keys():
            self.pi.write(gpio_pin, 0)
            self.pi.set_mode(gpio_pin, pigpio.OUTPUT)

            self.add_gpio_callback(gpio_pin)

    def set_value(self, do_pos: int, value: bool) -> None:
        for gpio, di in GPIO_DO_MAP.items():
            if di == do_pos:
                self.pi.write(gpio, value)
                return

    def get_value(self, dio_pos: int) -> Optional[bool]:
        for gpio, di in GPIO_DO_MAP.items():
            if di == dio_pos:
                return bool(self.pi.read(gpio))
        return None

    def get_all_values(self) -> list[bool]:
        result: list[bool] = []
        for gpio, di in GPIO_DO_MAP.items():
            result.append(bool(self.pi.read(gpio)))
        return result

    def handle_pin_status(self, gpio: int, level: int, tick) -> None:
        print(f"GPIO {gpio} changed to {level}")
        if self.callback is None:
            return
        di_pos = GPIO_DO_MAP.get(gpio, None)
        if di_pos is None:
            return
        self.callback(di_pos, level == 1)

    @property
    def io_count(self) -> int:
        return 3