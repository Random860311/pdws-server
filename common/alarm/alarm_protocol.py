from typing import Protocol


class AlarmProtocol(Protocol):
    def reset(self) -> None: ...

    @property
    def has_critical_alarm(self) -> bool: ...

    @property
    def has_alarm(self) -> bool: ...