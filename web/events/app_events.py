from enum import Enum


class EAppEvents(str, Enum):
    WARNING = "app:warning"
    ERROR = "app:error"

    STATION_EMIT_UPDATE = "station:emit_update"
