from typing import Optional, Sequence
import threading

from sqlalchemy import false

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.thread_manager_protocol import ThreadManagerProtocol
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol
from dto.device.sensor_dto import SensorConfigDto
from dto.station_dto import StationDto
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.io.events.di_event import DIEvent
from services.io.io_service_protocol import IOServiceProtocol
from station.alternatator.alternator_protocol import AlternatorProtocol
from station.starter.starter_protocol import StarterProtocol
from station.station_protocol import StationProtocol
from web.events.station.station_update_event import StationUpdateEvent


class Station(StationProtocol):
    def __init__(
            self,
            thread_manager: ThreadManagerProtocol,
            event_dispatcher: EventDispatcherProtocol,
            alternator: AlternatorProtocol,
            io_service: IOServiceProtocol,
            app_service: ApplicationServiceProtocol,
            starter: StarterProtocol,
            sensor_pressure: SensorProtocol,
            systems: Sequence[SystemProtocol],
            sensor_additional: Optional[SensorProtocol] = None,
    ) -> None:
        self.__thread_manager = thread_manager
        self.__event_dispatcher = event_dispatcher
        self.__abort_event = threading.Event()
        self.__io_service = io_service
        self.__app_service = app_service
        self.__alternator = alternator
        self.__starter = starter

        self.__sensor_pressure = sensor_pressure
        self.__sensor_additional = sensor_additional
        self.__systems: tuple[SystemProtocol, ...] = tuple(systems)

        self.__emergency_stop: bool = False

        event_dispatcher.subscribe(DIEvent, self.handle_di_change)

    def handle_di_change(self, event: DIEvent):
        match event.io_id:
            case self.__io_service.di_emergency_stop:
                self.handle_emergency_stop(event.value_new)

    @property
    def sensor_pressure(self) -> SensorProtocol:
        return self.__sensor_pressure

    @property
    def sensor_additional(self) -> Optional[SensorProtocol]:
        return self.__sensor_additional

    @property
    def systems(self) -> Sequence[SystemProtocol]:
        return self.__systems

    def get_system(self, device_id: int) -> Optional[SystemProtocol]:
        return next((sys for sys in self.systems if sys.device_id == device_id), None)

    def set_system_priority_hand(self, device_id: int, priority: ESystemPriority) -> None:
        sys = self.get_system(device_id)
        if sys is not None:
            sys.priority_hand = priority

    def set_system_mode(self, device_id: int, mode: ESystemMode) -> None:
        print("Emergency stop: ", self.__emergency_stop)
        if self.__emergency_stop:
            return
        sys = self.get_system(device_id)
        if sys is not None:
            sys.mode = mode

    def set_sensor_config(self, config: SensorConfigDto):
        if config.device_id == self.sensor_pressure.device_id:
            self.sensor_pressure.config = config
        elif self.sensor_additional and config.device_id == self.sensor_additional.device_id:
            self.sensor_additional.config = config

    def __worker(self):
        while not self.__abort_event.is_set():
            self.__io_service.scan()

            if not self.__emergency_stop:
                self.__alternator.alternate()
                self.__starter.execute()

            self.__emit_update()

            self.__abort_event.wait(0.5)

    def start(self):
        self.__abort_event.clear()
        self.__thread_manager.start_background_task(self.__worker)

    def stop(self):
        self.__abort_event.set()

    def handle_emergency_stop(self, value: bool) -> None:
        self.__emergency_stop = value
        for sys in self.systems:
            sys.set_emergency_stop(value)

    def __emit_update(self):
        systems_dto = [s.to_serializable() for s in self.systems]
        station_dto = StationDto(
            systems=systems_dto,
            pressure_sensor=self.sensor_pressure.to_serializable(),
            additional_sensor=self.sensor_additional.to_serializable() if self.sensor_additional is not None else None,
            io_status=self.__io_service.to_serializable(),
            app_settings=self.__app_service.to_serializable(),
            emergency_stop=self.__emergency_stop,
        )
        self.__event_dispatcher.emit_async(StationUpdateEvent(station_dto))