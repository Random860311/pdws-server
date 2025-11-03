from typing import TypedDict, Unpack

from common.kv_config import KVConfig
from services.application.application_service_protocol import ApplicationServiceProtocol

class ApplicationKwargs(TypedDict, total=False):
    system_count: int
    level_set_point: float
    level_offset: float
    start_pump_delay: int
    stop_pump_delay: int
    ai_max_raw: list[int]


class ApplicationService(ApplicationServiceProtocol):
    def __init__(self, **kwargs: Unpack[ApplicationKwargs]) -> None:
        self.__config = KVConfig(section="app")

        self.__config.set("system_count", kwargs.get("system_count", 3))
        self.__config.set("level_set_point", kwargs.get("level_set_point", 0.0))
        self.__config.set("level_offset", kwargs.get("level_offset", 0.0))
        self.__config.set("start_pump_delay", kwargs.get("start_pump_delay", 0))
        self.__config.set("stop_pump_delay", kwargs.get("stop_pump_delay", 0))

        ai_max_raw = kwargs.get("ai_max_raw", [])
        for i, value in enumerate(ai_max_raw):
            self.__config.set(f"ai_max_raw_{i}", value)

    @property
    def system_count(self) -> int:
        return self.__config.get_int("system_count", 3)

    @property
    def level_set_point(self) -> float:
        return self.__config.get_float("level_set_point", 0.0)

    @level_set_point.setter
    def level_set_point(self, value: float) -> None:
        self.__config.set("level_set_point", value)

    @property
    def level_offset(self) -> float:
        return self.__config.get_float("level_offset", 0.0)

    @level_offset.setter
    def level_offset(self, value: float) -> None:
        self.__config.set("level_offset", value)

    @property
    def start_pump_delay(self) -> int:
        return self.__config.get_int("start_pump_delay", 0)

    @start_pump_delay.setter
    def start_pump_delay(self, value: int) -> None:
        self.__config.set("start_pump_delay", value)

    @property
    def stop_pump_delay(self) -> int:
        return self.__config.get_int("stop_pump_delay", 0)

    @stop_pump_delay.setter
    def stop_pump_delay(self, value: int) -> None:
        self.__config.set("stop_pump_delay", value)

    def get_ai_max_raw(self, ai: int) -> int:
        return self.__config.get_int(f"ai_max_raw_{ai}", 0)

    def set_ai_max_raw(self, ai: int, value: int) -> None:
        self.__config.set(f"ai_max_raw_{ai}", value)