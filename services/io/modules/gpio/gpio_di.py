from typing import Optional, Callable, Tuple
import pigpio
from services.io.modules.di_module_protocol import DIModuleProtocol

GPIO_MAP: dict[int, int] = {
    23: 0,
    25: 1
}

class GPIO_DI(DIModuleProtocol):
    def __init__(self, pi: pigpio.pi):
        self.__pi = pi
        self.__callback: Optional[Callable[[int, bool], None]] = None

        self.__gpio_callbacks = []

        for gpio_pin in GPIO_MAP.keys():
            self.__pi.set_mode(gpio_pin, pigpio.INPUT)
            self.__pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)

            self.__add_gpio_callback(gpio_pin)

    @property
    def callback(self) -> Optional[Callable[[int, bool], None]]:
        return self.__callback

    @callback.setter
    def callback(self, value: Optional[Callable[[int, bool], None]]) -> None:
        self.__callback = value

    def get_value(self, di_pos: int) -> Optional[bool]:
        for gpio, di in GPIO_MAP.items():
            if di == di_pos:
                return bool(self.__pi.read(gpio))
        return None

    def get_all_values(self) -> list[bool]:
        result: list[bool] = []
        for gpio, di in GPIO_MAP.items():
            result.append(bool(self.__pi.read(gpio)))
        return result

    def __add_gpio_callback(self, gpio, edge=pigpio.EITHER_EDGE, steady=5000):
        gpio_callback = self.__pi.callback(gpio, edge, self.__handle_pin_status)
        self.__pi.set_glitch_filter(gpio, steady)

        self.__gpio_callbacks.append(gpio_callback)

    def __handle_pin_status(self, gpio: int, level: int, tick) -> None:
        print(f"GPIO {gpio} changed to {level}")
        if self.callback is None:
            return
        di_pos = GPIO_MAP.get(gpio, None)
        if di_pos is None:
            return
        self.callback(di_pos, level == 1)

    @property
    def io_count(self) -> int:
        return 3