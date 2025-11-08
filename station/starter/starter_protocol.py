from typing import Protocol


class StarterProtocol(Protocol):
    def execute(self) -> None: ...