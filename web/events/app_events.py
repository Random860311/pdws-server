from enum import Enum


class EAppEvents(str, Enum):
    WARNING = "app:warning"
    ERROR = "app:error"

    STATION_EMIT_UPDATE = "station:emit_update"
    STATION_SET_CONFIG = "station:set_config"

    SYSTEM_SET_MODE = "system:set_mode"

    SENSOR_SET_CONFIG = "sensor:set_config"