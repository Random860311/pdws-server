from enum import Enum
from typing import Optional

from common.kv_config import KVConfig
from dto.device.sensor_dto import SensorConfigDto
from services.device.device_service_protocol import DeviceServiceProtocol

class EConfigKey(str, Enum):
    ID = "id"

    RUN_TIME_TOTAL = "total_run_time"
    RUN_TIME_LAST = "last_run_time"

    SENSOR_VALUE_SCALED_MAX = "value_scaled_max"
    SENSOR_VALUE_SCALED_MIN = "value_scaled_min"
    SENSOR_AI_MAX = "ai_max"
    SENSOR_AI_MIN = "ai_min"
    SENSOR_ALARM_RESET = "alarm_reset"
    SENSOR_ALARM_START_DELAY = "alarm_start_delay"
    SENSOR_ALARM_STOP_DELAY = "alarm_stop_delay"
    SENSOR_ALARM_START_HIGH = "alarm_start_high"
    SENSOR_ALARM_STOP_HIGH = "alarm_stop_high"
    SENSOR_ALARM_START_HIGH_HIGH = "alarm_start_high_high"
    SENSOR_ALARM_STOP_HIGH_HIGH = "alarm_stop_high_high"

class DeviceService(DeviceServiceProtocol):
    def __init__(self):
        self.__configs: dict[str, KVConfig] = {}

    def get_device_total_run_time(self, device_name: str) -> float:
        config = self.get_config(device_name)
        return config.get_float(EConfigKey.RUN_TIME_TOTAL, 0.0)

    def set_device_total_run_time(self, device_name: str, run_time: float) -> None:
        config = self.get_config(device_name)
        config.set(EConfigKey.RUN_TIME_TOTAL, run_time)

    def add_device_total_run_time(self, device_name: str, run_time: float) -> float:
        current_total = self.get_device_total_run_time(device_name)
        new_total = current_total + run_time
        self.set_device_total_run_time(device_name, new_total)
        return new_total

    def get_device_last_run_time(self, device_name: str) -> float:
        config = self.get_config(device_name)
        return config.get_float(EConfigKey.RUN_TIME_LAST, 0.0)

    def set_device_last_run_time(self, device_name: str, run_time: float) -> None:
        config = self.get_config(device_name)
        config.set(EConfigKey.RUN_TIME_LAST, run_time)

    def clear_device_run_times(self, device_name: str) -> None:
        config = self.get_config(device_name)
        config.set(EConfigKey.RUN_TIME_TOTAL, 0.0)
        config.set(EConfigKey.RUN_TIME_LAST, 0.0)

    def get_config(self, device_name: str) -> KVConfig:
        if not device_name in self.__configs:
            self.__configs[device_name] = KVConfig(section=device_name)
        return self.__configs[device_name]

    def get_sensor_config(self, device_id: int, device_name: str, default: Optional[SensorConfigDto] = None) -> Optional[SensorConfigDto]:
        if not device_name in self.__configs:
            if default is None:
                return None
            else:
                self.set_sensor_config(device_name, default)
                return default

        config = self.get_config(device_name)
        return SensorConfigDto(
            device_id=device_id,
            device_name=device_name,
            value_scaled_max=config.get_float(EConfigKey.SENSOR_VALUE_SCALED_MAX, 0.0),
            value_scaled_min=config.get_float(EConfigKey.SENSOR_VALUE_SCALED_MIN, 0.0),
            ai_max=config.get_int(EConfigKey.SENSOR_AI_MAX, 0),
            ai_min=config.get_int(EConfigKey.SENSOR_AI_MIN, 0),
            need_alarm_reset=config.get_bool(EConfigKey.SENSOR_ALARM_RESET, False),
            alarm_start_delay=config.get_int(EConfigKey.SENSOR_ALARM_START_DELAY, 0),
            alarm_stop_delay=config.get_int(EConfigKey.SENSOR_ALARM_STOP_DELAY, 0),
            alarm_start_high=config.get_float(EConfigKey.SENSOR_ALARM_START_HIGH, 0.0),
            alarm_stop_high=config.get_float(EConfigKey.SENSOR_ALARM_STOP_HIGH, 0.0),
            alarm_start_high_high=config.get_float(EConfigKey.SENSOR_ALARM_START_HIGH_HIGH, 0.0),
            alarm_stop_high_high=config.get_float(EConfigKey.SENSOR_ALARM_STOP_HIGH_HIGH, 0.0)
        )

    def set_sensor_config(self, device_name: str, sensor: SensorConfigDto) -> None:
        config = self.get_config(device_name)
        config.set(EConfigKey.SENSOR_VALUE_SCALED_MAX, sensor.value_scaled_max)
        config.set(EConfigKey.SENSOR_VALUE_SCALED_MIN, sensor.value_scaled_min)
        config.set(EConfigKey.SENSOR_AI_MAX, sensor.ai_max)
        config.set(EConfigKey.SENSOR_AI_MIN, sensor.ai_min)
        config.set(EConfigKey.SENSOR_ALARM_RESET, sensor.need_alarm_reset)
        config.set(EConfigKey.SENSOR_ALARM_START_DELAY, sensor.alarm_start_delay)
        config.set(EConfigKey.SENSOR_ALARM_STOP_DELAY, sensor.alarm_stop_delay)
        config.set(EConfigKey.SENSOR_ALARM_START_HIGH, sensor.alarm_start_high)
        config.set(EConfigKey.SENSOR_ALARM_STOP_HIGH, sensor.alarm_stop_high)
        config.set(EConfigKey.SENSOR_ALARM_START_HIGH_HIGH, sensor.alarm_start_high_high)
        config.set(EConfigKey.SENSOR_ALARM_STOP_HIGH_HIGH, sensor.alarm_stop_high_high)