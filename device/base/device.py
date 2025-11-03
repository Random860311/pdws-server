from abc import ABC, abstractmethod

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol

from device.base.device_protocol import DeviceProtocol
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.io_service_protocol import IOServiceProtocol


class Device(DeviceProtocol, ABC):
    def __init__(self, device_id: int, device_service: DeviceServiceProtocol, io_service: IOServiceProtocol, event_dispatcher: EventDispatcherProtocol) -> None:
        self.__device_id = device_id
        self.__device_service = device_service
        self.__io_service = io_service
        self.__event_dispatcher = event_dispatcher

    @property
    def device_id(self) -> int:
        return int(self.__device_id)

    @property
    @abstractmethod
    def device_name(self) -> str:
        pass

    def reset(self) -> None:
        pass

    @property
    def has_critical_alarm(self) -> bool:
        return False

    @property
    def has_alarm(self) -> bool:
        return self.has_critical_alarm

    @property
    def event_dispatcher(self) -> EventDispatcherProtocol:
        return self.__event_dispatcher

    @property
    def device_service(self) -> DeviceServiceProtocol:
        return self.__device_service

    @property
    def io_service(self) -> IOServiceProtocol:
        return self.__io_service