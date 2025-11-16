from dataclasses import dataclass, field

from dto.base_dto import BaseDto


@dataclass
class ApplicationDto(BaseDto):
    level_set_point: float
    level_offset: float
    system_count: int = field(kw_only=True, default=3)
    start_pump_delay: int = field(kw_only=True, default=5)
    stop_pump_delay: int = field(kw_only=True, default=5)
    system_fail_to_start_delay: int = field(kw_only=True, default=0)
