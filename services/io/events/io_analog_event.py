from dataclasses import dataclass
from typing import Optional

from services.io.events.io_event import IOEvent


@dataclass
class IOAnalogEvent(IOEvent):
    value_old: Optional[int]
    value_new: int
