from dataclasses import dataclass

from services.io.events.io_digital_event import IODigitalEvent


@dataclass
class DOEvent(IODigitalEvent):
    pass
