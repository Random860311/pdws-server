from typing import TypedDict, Unpack

from common.kv_config import KVConfig
from core.serializable_protocol import SerializableProtocol
from dto.application.application_dto import ApplicationDto
from services.application.application_service_protocol import ApplicationServiceProtocol

class ApplicationService(ApplicationServiceProtocol):
    def __init__(self, config: ApplicationDto) -> None:
        self.__config = KVConfig(section="app")

        merged = config.to_dict() | self.__config.items()

        self.update_config(ApplicationDto(**merged))

    def update_config(self, config: ApplicationDto) -> None:
        print(f"Updating application config: {config}")
        self.__config.set("system_count", config.system_count if config.system_count else 3)
        self.__config.set("level_set_point", config.level_set_point if config.level_set_point else 0.0)
        self.__config.set("level_offset", config.level_offset if config.level_offset else 0.0)
        self.__config.set("start_pump_delay", config.start_pump_delay if config.start_pump_delay else 0)
        self.__config.set("stop_pump_delay", config.stop_pump_delay if config.stop_pump_delay else 0)

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

    def to_serializable(self) -> SerializableProtocol:
        return ApplicationDto(
            system_count=self.system_count,
            level_set_point=self.level_set_point,
            level_offset=self.level_offset,
            start_pump_delay=self.start_pump_delay,
            stop_pump_delay=self.stop_pump_delay,
        )