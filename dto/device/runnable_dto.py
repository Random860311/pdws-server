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