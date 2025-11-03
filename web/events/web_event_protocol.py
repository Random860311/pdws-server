from typing import Protocol

from core.serializable_protocol import SerializableProtocol


class WebEventProtocol(Protocol):
    @property
    def event_name(self) -> str: ...

    @property
    def data(self) -> SerializableProtocol: ...