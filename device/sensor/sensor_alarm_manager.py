import time

from common.alarm.alarm_protocol import AlarmProtocol


class SensorAlarManager(AlarmProtocol):
    def __init__(self, need_reset: bool = False):
        self.__value = 0.0

        self.__start_delay = 0
        self.__stop_delay = 0

        self.__start_high = 0.0
        self.__start_high_high = 0.0
        self.__stop_high = 0.0
        self.__stop_high_high = 0.0

        self.__need_reset = need_reset

        self.__start_high_time = 0.0
        self.__start_high_high_time = 0.0
        self.__stop_high_time = 0.0
        self.__stop_high_high_time = 0.0

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

        if self.has_alarm:
            self.__stop_high_time = 0.0

        if self.has_critical_alarm:
            self.__stop_high_high_time = 0.0

        if (self.stop_high_elapsed_time > self.stop_delay) and (not self.__need_reset):
            self.__start_high_time = 0.0

        if (self.stop_high_high_elapsed_time > self.stop_delay) and (not self.__need_reset):
            self.__start_high_high_time = 0.0

    @property
    def start_delay(self) -> int:
        return self.__start_delay

    @start_delay.setter
    def start_delay(self, value: int) -> None:
        self.__start_delay = value

    @property
    def stop_delay(self) -> int:
        return self.__stop_delay

    @stop_delay.setter
    def stop_delay(self, value: int) -> None:
        self.__stop_delay = value

    @property
    def start_high(self) -> float:
        return self.__start_high

    @start_high.setter
    def start_high(self, value: float) -> None:
        self.__start_high = value

    @property
    def start_high_high(self) -> float:
        return self.__start_high_high

    @start_high_high.setter
    def start_high_high(self, value: float) -> None:
        self.__start_high_high = value

    @property
    def stop_high(self) -> float:
        return self.__stop_high

    @stop_high.setter
    def stop_high(self, value: float) -> None:
        self.__stop_high = value

    @property
    def stop_high_high(self) -> float:
        return self.__stop_high_high

    @stop_high_high.setter
    def stop_high_high(self, value: float) -> None:
        self.__stop_high_high = value

    @property
    def has_alarm(self) -> bool:
        return self.start_high_elapsed_time > self.__start_delay

    @property
    def has_critical_alarm(self) -> bool:
        return self.start_high_high_elapsed_time > self.__start_delay

    def reset(self) -> None:
        if self.stop_high_elapsed_time > self.stop_delay:
            self.__start_high_time = 0.0

        if self.stop_high_high_elapsed_time > self.stop_delay:
            self.__start_high_high_time = 0.0


