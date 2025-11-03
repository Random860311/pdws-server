from dataclasses import dataclass, field
from typing import Optional

from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority
from dto.device.contactor_dto import ContactorDto
from dto.device.pump_dto import PumpDto
from dto.device.runnable_dto import RunnableDto


@dataclass
class SystemDto(RunnableDto):
    mode: int = field(kw_only=True, default=ESystemMode.OFF.value)
    priority: int = field(kw_only=True, default=ESystemPriority.OUT.value)
    priority_auto: int = field(kw_only=True, default=ESystemPriority.OUT.value)
    priority_hand: int = field(kw_only=True, default=ESystemPriority.OUT.value)

    contactor: Optional[ContactorDto] = field(kw_only=True, default=None)
    pump: Optional[PumpDto] = field(kw_only=True, default=None)