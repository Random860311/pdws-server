from typing import Protocol


class IOModuleProtocol(Protocol):
    def cleanup(self) -> None: ...

    @property
    def io_count(self) -> int: ...