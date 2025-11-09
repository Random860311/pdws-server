from dataclasses import dataclass, field
from typing import Optional

from core.serializable_protocol import SerializableProtocol
from dto.base_dto import BaseDto


@dataclass
class StationDto(BaseDto):
    systems: list[SerializableProtocol]
    pressure_sensor: SerializableProtocol
    additional_sensor: Optional[SerializableProtocol] = field(kw_only=True, default=None)
    io_status: SerializableProtocol
    app_settings: SerializableProtocol