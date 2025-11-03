from typing import Protocol, runtime_checkable

from device.base.device_runnable_protocol import DeviceRunnableProtocol
from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority


@runtime_checkable
class SystemProtocol(DeviceRunnableProtocol, Protocol):
    @property
    def mode(self) -> ESystemMode: ...

    @mode.setter
    def mode(self, value: ESystemMode) -> None: ...

    @property
    def priority(self) -> ESystemPriority: ...

    @property
    def priority_auto(self) -> ESystemPriority: ...

    @priority_auto.setter
    def priority_auto(self, value: ESystemPriority) -> None: ...

    @property
    def priority_hand(self) -> ESystemPriority:...

    @priority_hand.setter
    def priority_hand(self, value: ESystemPriority) -> None: ...



