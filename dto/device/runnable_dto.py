from dataclasses import dataclass, field

from device.base.device_status import EDeviceStatus
from dto.device.device_dto import DeviceDto


@dataclass
class RunnableDto(DeviceDto):
    status: int = field(kw_only=True, default=EDeviceStatus.STOPPED.value)
    can_run: bool = field(kw_only=True, default=False)
    can_run_auto: bool = field(kw_only=True, default=False)
    call_to_run: bool = field(kw_only=True, default=False)
    alarm_fail_to_start: bool = field(kw_only=True, default=False)

    emergency_stop: bool = field(kw_only=True, default=False)

    run_time_current: float = field(kw_only=True, default=0.0)
    run_time_last: float = field(kw_only=True, default=0.0)
    run_time_total: float = field(kw_only=True, default=0.0)
