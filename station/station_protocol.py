from typing import Protocol, Optional, Sequence

from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol


class StationProtocol(Protocol):
    @property
    def sensor_pressure(self) -> SensorProtocol: ...

    @property
    def sensor_additional(self) -> Optional[SensorProtocol]: ...

    @property
    def systems(self) -> Sequence[SystemProtocol]:...

    def get_system(self, device_id: int) -> Optional[SystemProtocol]: ...

    def set_system_priority_hand(self, device_id: int, priority: ESystemPriority) -> None: ...

    def set_system_mode(self, device_id: int, mode: ESystemMode) -> None: ...

    def start(self): ...

    def stop(self): ...
