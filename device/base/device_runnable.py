import threading
import time
from abc import ABC, abstractmethod

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from device.base.device_runnable_protocol import DeviceRunnableProtocol
from device.base.device import Device
from device.base.device_status import EDeviceStatus
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.events.di_event import DIEvent
from services.io.io_service_protocol import IOServiceProtocol


class DeviceRunnable(DeviceRunnableProtocol, Device, ABC):
    def __init__(self, device_id: int, device_service: DeviceServiceProtocol, io_service: IOServiceProtocol, event_dispatcher: EventDispatcherProtocol, app_service: ApplicationServiceProtocol):
        super().__init__(device_id, device_service, io_service, event_dispatcher, app_service)

        self.__status = EDeviceStatus.STOPPED
        self._emergency_stop = False

        self.__alarm_fail_to_start_time = 0.0
        self.__current_run_start_time = 0.0

    @property
    def status(self) -> EDeviceStatus:
        return self.__status

    @status.setter
    def status(self, value: EDeviceStatus) -> None:
        if self.__status == value:
            return
        self.__status = value

        if self.__status == EDeviceStatus.RUNNING:
            self.__alarm_fail_to_start_time = 0.0
            self.__current_run_start_time = time.perf_counter()
        if self.__status == EDeviceStatus.STOPPED:
            current = round(self.run_time_current, 2)
            self.device_service.add_device_total_run_time(self.device_name, current)
            self.device_service.set_device_last_run_time(self.device_name, current)
            self.__current_run_start_time = 0.0

    @property
    def can_run(self) -> bool:
        return (not self.has_critical_alarm) and (not self._emergency_stop)

    @property
    def can_run_auto(self) -> bool:
        return self.can_run

    @abstractmethod
    def call_to_run(self) -> None:
        delay = self.app_service.system_fail_to_start_delay
        if self.__alarm_fail_to_start_time == 0.0 and delay > 0:
            self.__alarm_fail_to_start_time = time.perf_counter()

    @abstractmethod
    def stop(self) -> None:
        self.__alarm_fail_to_start_time = 0.0

    def set_emergency_stop(self, value: bool) -> None:
        if self._emergency_stop == value:
            return
        self._emergency_stop = value
        self.stop()

    @property
    def alarm_fail_to_start(self) -> bool:
        delay = self.app_service.system_fail_to_start_delay
        if delay == 0 or self.__alarm_fail_to_start_time == 0.0:
            return False
        else:
            return (time.perf_counter() - self.__alarm_fail_to_start_time) > delay

    @property
    def has_alarm(self) -> bool:
        return super().has_alarm or self.alarm_fail_to_start

    @property
    def run_time_current(self) -> float:
        return 0.0 if self.__current_run_start_time == 0.0 else time.perf_counter() - self.__current_run_start_time

    @property
    def run_time_last(self) -> float:
        return self.device_service.get_device_last_run_time(self.device_name)

    @property
    def run_time_total(self) -> float:
        return self.device_service.get_device_total_run_time(self.device_name) + self.run_time_current

    def reset_run_time(self) -> None:
        self.__current_run_start_time = 0.0
        self.device_service.clear_device_run_times(self.device_name)

    def handle_di_change(self, event: DIEvent):
        match event.io_id:
            case self.io_service.di_emergency_stop:
                self.set_emergency_stop(event.value_new)