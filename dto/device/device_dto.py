from dataclasses import dataclass, field

from dto.base_dto import BaseDto


@dataclass
class DeviceDto(BaseDto):
    device_id: int = field(kw_only=True, default=0)
    device_name: str = field(kw_only=True, default="")
    has_critical_alarm: bool = field(kw_only=True, default=False)
    has_alarm: bool = field(kw_only=True, default=False)
