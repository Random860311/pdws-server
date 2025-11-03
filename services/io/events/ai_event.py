from dataclasses import dataclass

from services.io.events.io_analog_event import IOAnalogEvent


@dataclass
class AIEvent(IOAnalogEvent):
    pass
