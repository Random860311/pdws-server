from typing import TypedDict

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from device.base.device_runnable import DeviceRunnable
from device.base.device_status import EDeviceStatus
from device.contactor.contactor_protocol import ContactorProtocol
from dto.device.contactor_dto import ContactorDto
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.events.di_event import DIEvent
from services.io.io_service_protocol import IOServiceProtocol


class ContactorKwargs(TypedDict, total=False):
    di_running: int
    do_run: int

class Contactor(ContactorProtocol, DeviceRunnable):
    def __init__(
            self,
            device_id: int,
            device_service: DeviceServiceProtocol,
            io_service: IOServiceProtocol,
            event_dispatcher: EventDispatcherProtocol,
            app_service: ApplicationServiceProtocol,
            di_running: int,
            do_run: int
    ):
        super().__init__(device_id, device_service, io_service, event_dispatcher, app_service)

        self.__di_running = di_running
        self.__do_run = do_run

        event_dispatcher.subscribe(DIEvent, self.handle_di_change)

    @property
    def device_name(self) -> str:
        return f"contactor_{self.device_id}"

    @property
    def di_running(self) -> int:
        return self.__di_running

    @property
    def do_run(self) -> int:
        return self.__do_run

    @property
    def is_called_to_run(self) -> bool:
        return self.io_service.get_digital_output_value(self.do_run)

    def handle_di_change(self, event: DIEvent):
        match event.io_id:
            case self.di_running:
                self.status = EDeviceStatus.RUNNING if event.value_new else EDeviceStatus.STOPPED
                # print(f"Contactor {self.device_name} status: {self.status}")
            case _:
                super().handle_di_change(event)

    def call_to_run(self) -> None:
        if not self.can_run and self.status != EDeviceStatus.RUNNING:
            return
        self.io_service.set_digital_output_value(self.do_run, True)
        super().call_to_run()

    def stop(self) -> None:
        super().stop()
        self.io_service.set_digital_output_value(self.do_run, False)

    def to_serializable(self) -> SerializableProtocol:
        return ContactorDto(
            device_id=self.device_id,
            device_name=self.device_name,
            has_critical_alarm=self.has_critical_alarm,
            has_alarm=self.has_alarm,

            status=self.status,
            can_run=self.can_run,
            can_run_auto=self.can_run_auto,
            call_to_run=self.is_called_to_run,
            alarm_fail_to_start=self.alarm_fail_to_start,
            emergency_stop=self._emergency_stop,
            run_time_current=self.run_time_current,
            run_time_last=self.run_time_last,
            run_time_total=self.run_time_total,
        )