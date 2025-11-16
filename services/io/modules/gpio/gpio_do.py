import pigpio

from services.io.modules.gpio.gpio_map import GPIO_DO_MAP
from services.io.modules.do_module_protocol import DOModuleProtocol
from services.io.modules.gpio.gpio_dio import GpioDio


class GPIO_DO(DOModuleProtocol, GpioDio):

    def __init__(self, pi: pigpio.pi):
        super().__init__(pi)

    @property
    def dio_map(self) -> dict[int, int]:
        return GPIO_DO_MAP

    def initialize(self) -> None:
        for gpio_pin in GPIO_DO_MAP.keys():
            self.pi.write(gpio_pin, 0)
            self.pi.set_mode(gpio_pin, pigpio.OUTPUT)

            self.add_gpio_callback(gpio_pin)

    def set_value(self, do_pos: int, value: bool) -> None:
        for gpio, di in self.dio_map.items():
            if di == do_pos:
                # print(f"Set GPIO DO: {do_pos}, Value: {value}")
                self.pi.write(gpio, value)
                return

    def handle_pin_status(self, gpio: int, level: int, tick) -> None:
        # print(f"GPIO {gpio} changed to {level}")
        if self.callback is None:
            return
        di_pos = self.dio_map.get(gpio, None)
        if di_pos is None:
            return
        self.callback(di_pos, level == 1)