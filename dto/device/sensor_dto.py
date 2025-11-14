from dataclasses import dataclass, field

from dto.device.device_dto import DeviceDto

@dataclass
class SensorConfigDto(DeviceDto):
    value_scaled_max: float = field(kw_only=True, default=0.0)
    value_scaled_min: float = field(kw_only=True, default=0.0)

    ai_max: int = field(kw_only=True, default=0)
    ai_min: int = field(kw_only=True, default=0)

    need_alarm_reset: bool = field(kw_only=True, default=False)

    alarm_start_delay: int = field(kw_only=True, default=0)
    alarm_stop_delay: int = field(kw_only=True, default=0)

    alarm_start_high: float = field(kw_only=True, default=0.0)
    alarm_stop_high: float = field(kw_only=True, default=0.0)

    alarm_start_high_high: float = field(kw_only=True, default=0.0)
    alarm_stop_high_high: float = field(kw_only=True, default=0.0)

    alarm_start_low: float = field(kw_only=True, default=0.0)
    alarm_stop_low: float = field(kw_only=True, default=0.0)

    alarm_start_low_low: float = field(kw_only=True, default=0.0)
    alarm_stop_low_low: float = field(kw_only=True, default=0.0)

    is_high_high_critical: bool = field(kw_only=True, default=True)
    is_low_low_critical: bool = field(kw_only=True, default=True)

    adjustment: float = field(kw_only=True, default=0.0)

@dataclass
class SensorDto(SensorConfigDto):
    value_scaled: float
    value_ai: int
    value_ma: float

    is_high_active: bool = field(kw_only=True, default=False)
    is_high_high_active: bool = field(kw_only=True, default=False)
    is_low_active: bool = field(kw_only=True, default=False)
    is_low_low_active: bool = field(kw_only=True, default=False)
