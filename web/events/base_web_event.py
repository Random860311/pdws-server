from abc import ABC

from core.serializable_protocol import SerializableProtocol
from web.events.web_event_protocol import WebEventProtocol


class BaseWebEvent(WebEventProtocol, ABC):
    def __init__(self, event_name: str, event_data: SerializableProtocol) -> None:
        self.__event_name = event_name
        self.__event_data = event_data

    @property
    def event_name(self) -> str:
        return self.__event_name

    @property
    def data(self) -> SerializableProtocol:
        return self.__event_data
