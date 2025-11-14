import time

from common.alarm.alarm_protocol import AlarmProtocol
from dto.device.sensor_dto import SensorConfigDto


class SensorConfigManager(AlarmProtocol):
    def __init__(self, config: SensorConfigDto):
        self.__value = 0.0

        self.__config = config

        self.__start_high_time = 0.0
        self.__start_high_high_time = 0.0
        self.__stop_high_time = 0.0
        self.__stop_high_high_time = 0.0

        self.__start_low_time = 0.0
        self.__start_low_low_time = 0.0
        self.__stop_low_time = 0.0
        self.__stop_low_low_time = 0.0

    @property
    def config(self) -> SensorConfigDto:
        return self.__config
    @config.setter
    def config(self, value: SensorConfigDto) -> None:
        self.__config = value

    @property
    def start_high_elapsed_time(self) -> float:
        return 0 if self.__start_high_time == 0 else time.perf_counter() - self.__start_high_time

    @property
    def stop_high_elapsed_time(self) -> float:
        return 0 if self.__stop_high_time == 0 else time.perf_counter() - self.__stop_high_time

    @property
    def start_high_high_elapsed_time(self) -> float:
        return 0 if self.__start_high_high_time == 0 else time.perf_counter() - self.__start_high_high_time

    @property
    def stop_high_high_elapsed_time(self) -> float:
        return 0 if self.__stop_high_high_time == 0 else time.perf_counter() - self.__stop_high_high_time

    @property
    def start_low_elapsed_time(self) -> float:
        return 0 if self.__start_low_time == 0 else time.perf_counter() - self.__start_low_time

    @property
    def stop_low_elapsed_time(self) -> float:
        return 0 if self.__stop_low_time == 0 else time.perf_counter() - self.__stop_low_time

    @property
    def start_low_low_elapsed_time(self) -> float:
        return 0 if self.__start_low_low_time == 0 else time.perf_counter() - self.__start_low_low_time

    @property
    def stop_low_low_elapsed_time(self) -> float:
        return 0 if self.__stop_low_low_time == 0 else time.perf_counter() - self.__stop_low_low_time

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, value: float) -> None:
        self.__value = value

        if (0 < self.start_high <= value) and (self.__start_high_time == 0.0):
            self.__start_high_time = time.perf_counter()
            self.__stop_high_time = 0.0
        if (0 < self.stop_high >= value) and (self.__stop_high_time == 0.0):
            self.__stop_high_time = time.perf_counter()

        if (0 < self.start_high_high <= value) and (self.__start_high_high_time == 0.0):
            self.__start_high_high_time = time.perf_counter()
            self.__stop_high_high_time = 0.0
        if (0 < self.stop_high_high >= value) and (self.__stop_high_high_time == 0.0):
            self.__stop_high_high_time = time.perf_counter()

        if (0 < self.start_low > value) and (self.__start_low_time == 0.0):
            self.__start_low_time = time.perf_counter()
            self.__stop_low_time = 0.0
        if (0 < self.stop_low < value) and (self.__stop_low_time == 0.0):
            self.__stop_low_time = time.perf_counter()

        if (0 < self.start_low_low > value) and (self.__start_low_low_time == 0.0):
            self.__start_low_low_time = time.perf_counter()
            self.__stop_low_low_time = 0.0
        if (0 < self.stop_low_low < value) and (self.__stop_low_low_time == 0.0):
            self.__stop_low_low_time = time.perf_counter()

        if (self.stop_high_elapsed_time > self.stop_delay) and (not self.need_reset):
            self.__start_high_time = 0.0

        if (self.stop_high_high_elapsed_time > self.stop_delay) and (not self.need_reset):
            self.__start_high_high_time = 0.0

        if (self.stop_low_elapsed_time > self.stop_delay) and (not self.need_reset):
            self.__start_low_time = 0.0

        if (self.stop_low_low_elapsed_time > self.stop_delay) and (not self.need_reset):
            self.__start_low_low_time = 0.0

    @property
    def need_reset(self) -> bool:
        return self.__config.need_alarm_reset

    @property
    def start_delay(self) -> int:
        return self.__config.alarm_start_delay
    @start_delay.setter
    def start_delay(self, value: int) -> None:
        self.__config.alarm_start_delay = value

    @property
    def stop_delay(self) -> int:
        return self.__config.alarm_stop_delay
    @stop_delay.setter
    def stop_delay(self, value: int) -> None:
        self.__config.alarm_stop_delay = value

    @property
    def start_high(self) -> float:
        return self.__config.alarm_start_high
    @start_high.setter
    def start_high(self, value: float) -> None:
        self.__config.alarm_start_high = value

    @property
    def start_high_high(self) -> float:
        return self.__config.alarm_start_high_high
    @start_high_high.setter
    def start_high_high(self, value: float) -> None:
        self.__config.alarm_start_high_high = value

    @property
    def stop_high(self) -> float:
        return self.__config.alarm_stop_high
    @stop_high.setter
    def stop_high(self, value: float) -> None:
        self.__config.alarm_stop_high = value

    @property
    def stop_high_high(self) -> float:
        return self.__config.alarm_stop_high_high
    @stop_high_high.setter
    def stop_high_high(self, value: float) -> None:
        self.__config.alarm_stop_high_high = value

    @property
    def start_low(self) -> float:
        return self.__config.alarm_start_low
    @start_low.setter
    def start_low(self, value: float) -> None:
        self.__config.alarm_start_low = value

    @property
    def start_low_low(self) -> float:
        return self.__config.alarm_start_low_low
    @start_low_low.setter
    def start_low_low(self, value: float) -> None:
        self.__config.alarm_start_low_low = value

    @property
    def stop_low(self) -> float:
        return self.__config.alarm_stop_low
    @stop_low.setter
    def stop_low(self, value: float) -> None:
        self.__config.alarm_stop_low = value

    @property
    def stop_low_low(self) -> float:
        return self.__config.alarm_stop_low_low
    @stop_low_low.setter
    def stop_low_low(self, value: float) -> None:
        self.__config.alarm_stop_low_low = value

    @property
    def is_high_active(self) -> bool:
        return self.start_high_elapsed_time > self.start_delay
    @property
    def is_high_high_active(self) -> bool:
        return self.start_high_high_elapsed_time > self.start_delay

    @property
    def is_low_active(self) -> bool:
        return self.start_low_elapsed_time > self.start_delay
    @property
    def is_low_low_active(self) -> bool:
        return self.start_low_low_elapsed_time > self.start_delay

    @property
    def has_alarm(self) -> bool:
        return self.is_high_active or self.is_high_high_active or self.is_low_active or self.is_low_low_active

    @property
    def has_critical_alarm(self) -> bool:
        return (self.is_high_high_active and self.is_high_high_critical) or (self.is_low_low_active and self.is_low_low_critical)

    @property
    def is_high_high_critical(self) -> bool:
        return self.__config.is_high_high_critical

    @property
    def is_low_low_critical(self) -> bool:
        return self.__config.is_low_low_critical

    def reset(self) -> None:
        if self.stop_high_elapsed_time > self.stop_delay:
            self.__start_high_time = 0.0

        if self.stop_high_high_elapsed_time > self.stop_delay:
            self.__start_high_high_time = 0.0


