from dataclasses import dataclass
from typing import Optional

from services.io.events.io_event import IOEvent


@dataclass
class IODigitalEvent(IOEvent):
    value_old: Optional[bool]
    value_new: bool
