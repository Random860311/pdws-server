from abc import ABC, abstractmethod
from typing import Optional, Callable

import pigpio


class GpioDio(ABC):
    def __init__(self, pi: pigpio.pi):
        self.__pi = pi
        self.__callback: Optional[Callable[[int, bool], None]] = None

        self.__gpio_callbacks = []

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