from typing import Protocol, Sequence, Tuple

from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol


class AlternatorProtocol(Protocol):
    def alternate(self) -> None: ...