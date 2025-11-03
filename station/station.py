from typing import Optional, Sequence
import threading

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.thread_manager_protocol import ThreadManagerProtocol
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol
from dto.station_dto import StationDto
from services.io.io_service_protocol import IOServiceProtocol
from station.alternatator.alternator_protocol import AlternatorProtocol
from station.starter.StarterProtocol import StarterProtocol
from station.station_protocol import StationProtocol
from web.events.station.station_update_event import StationUpdateEvent


class Station(StationProtocol):
    def __init__(
            self,
            thread_manager: ThreadManagerProtocol,
            event_dispatcher: EventDispatcherProtocol,
            alternator: AlternatorProtocol,
            io_service: IOServiceProtocol,
            starter: StarterProtocol,
            sensor_pressure: SensorProtocol,
            systems: Sequence[SystemProtocol],
            sensor_additional: Optional[SensorProtocol] = None,
    ) -> None:
        self.__thread_manager = thread_manager
        self.__event_dispatcher = event_dispatcher
        self.__abort_event = threading.Event()
        self.__io_service = io_service
        self.__alternator = alternator
        self.__starter = starter

        self.__sensor_pressure = sensor_pressure
        self.__sensor_additional = sensor_additional
        self.__systems: tuple[SystemProtocol, ...] = tuple(systems)

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
        sys = self.get_system(device_id)
        if sys is not None:
            sys.mode = mode

    def __worker(self):
        while not self.__abort_event.is_set():
            self.__io_service.scan()
            self.__alternator.alternate()
            self.__starter.execute()

            self.__emit_update()

            self.__abort_event.wait(0.5)

    def start(self):
        self.__abort_event.clear()
        self.__thread_manager.start_background_task(self.__worker)

    def stop(self):
        self.__abort_event.set()

    def __emit_update(self):
        systems_dto = [s.to_serializable() for s in self.systems]
        station_dto = StationDto(
            systems=systems_dto,
            pressure_sensor=self.sensor_pressure.to_serializable(),
            additional_sensor=self.sensor_additional.to_serializable() if self.sensor_additional is not None else None,
            io_status=self.__io_service.to_serializable(),
        )
        self.__event_dispatcher.emit_async(StationUpdateEvent(station_dto))
        # import json

        # print(json.dumps(station_dto.to_dict(), indent=3))