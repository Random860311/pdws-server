from abc import ABC, abstractmethod
from typing import Sequence, Optional

from device.base.device_status import EDeviceStatus
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_protocol import SystemProtocol
from services.application.application_service_protocol import ApplicationServiceProtocol
from station.starter.StarterProtocol import StarterProtocol


class BaseStarter(StarterProtocol, ABC):
    def __init__(self, app_service: ApplicationServiceProtocol, sensor: SensorProtocol, systems: Sequence[SystemProtocol]):
        self.__app_service = app_service
        self.__sensor = sensor
        self.__systems = systems
        self.__start_call_time = 0.0
        self.__stop_call_time = 0.0

    @property
    def app_service(self) -> ApplicationServiceProtocol:
        return self.__app_service

    @property
    def systems(self) -> Sequence[SystemProtocol]:
        return self.__systems

    @property
    def start_call_time(self) -> float:
        return self.__start_call_time

    @start_call_time.setter
    def start_call_time(self, value: float) -> None:
        self.__start_call_time = value

    @property
    def stop_call_time(self) -> float:
        return self.__stop_call_time

    @stop_call_time.setter
    def stop_call_time(self, value: float) -> None:
        self.__stop_call_time = value

    @property
    def sensor(self) -> SensorProtocol:
        return self.__sensor

    @property
    def set_point(self) -> float:
        return self.app_service.level_set_point

    @property
    def offset(self) -> float:
        return self.app_service.level_offset

    @property
    def start_delay(self) -> int:
        return self.app_service.start_pump_delay

    @property
    def stop_delay(self) -> int:
        return self.app_service.stop_pump_delay

    @abstractmethod
    def should_start(self) -> bool:
        pass

    @abstractmethod
    def should_stop(self) -> bool:
        pass

    def get_next_stopped_system(self) -> Optional[SystemProtocol]:
        candidates = [sys for sys in self.systems if sys.can_run_auto and sys.status == EDeviceStatus.STOPPED]
        if not candidates:
            return None
        system = candidates[0]
        for sys in candidates:
            if system.priority_auto < sys.priority_auto:
                system = sys
        return system

    def get_last_running_system(self) -> Optional[SystemProtocol]:
        candidates = [sys for sys in self.systems if sys.can_run_auto and sys.status == EDeviceStatus.RUNNING]
        if not candidates:
            return None
        system = candidates[0]
        for sys in candidates:
            if system.priority_auto > sys.priority_auto:
                system = sys
        return system

    def execute(self) -> None:
        if self.should_start():
            # print("Should start")
            system = self.get_next_stopped_system()
            if system is not None:
                system.call_to_run()
            self.start_call_time = 0.0

        if self.should_stop():
            # print("Should stop")
            system = self.get_last_running_system()
            if system is not None:
                system.stop()
            self.stop_call_time = 0.0

