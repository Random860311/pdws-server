from abc import ABC, abstractmethod
from typing import Optional, Callable

import pigpio

from services.io.modules.digital_module_protocol import DigitalModuleProtocol


class GpioDio(DigitalModuleProtocol, ABC):
    def __init__(self, pi: pigpio.pi):
        self.__pi = pi
        self.__callback: Optional[Callable[[int, bool], None]] = None

        self.__gpio_callbacks = []

    @property
    @abstractmethod
    def dio_map(self) -> dict[int, int]:
        pass

    @property
    def pi(self) -> pigpio.pi:
        return self.__pi

    @property
    def callback(self) -> Optional[Callable[[int, bool], None]]:
        return self.__callback

    @callback.setter
    def callback(self, value: Optional[Callable[[int, bool], None]]) -> None:
        self.__callback = value

    def add_gpio_callback(self, gpio, edge=pigpio.EITHER_EDGE, steady=5000):
        gpio_callback = self.pi.callback(gpio, edge, self.handle_pin_status)
        self.pi.set_glitch_filter(gpio, steady)

        self.__gpio_callbacks.append(gpio_callback)

    @abstractmethod
    def handle_pin_status(self, gpio: int, level: int, tick) -> None:
        pass

    def get_all_values(self) -> list[bool]:
        result: list[bool] = []
        for gpio, di in self.dio_map.items():
            result.append(bool(self.pi.read(gpio)))
        return result

    @property
    def io_count(self) -> int:
        return len(self.dio_map)

    def get_value(self, pos: int) -> Optional[bool]:
        for gpio, di in self.dio_map.items():
            if di == pos:
                return bool(self.pi.read(gpio))
        return None

    def cleanup(self) -> None:
        for gpio_callback in self.__gpio_callbacks:
            gpio_callback.cancel()

    def is_managed_pos(self, io_pos: int) -> bool:
        return io_pos in self.dio_map.values()