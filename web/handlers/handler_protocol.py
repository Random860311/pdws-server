from typing import Protocol


class HandlerProtocol(Protocol):
    def register(self): ...