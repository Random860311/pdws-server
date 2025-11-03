from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SerializableProtocol(Protocol):
    def to_dict(self) -> dict[str, Any]: ...