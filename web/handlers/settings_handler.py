from flask_socketio import SocketIO

from common import utils
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from dto.application.application_dto import ApplicationDto
from dto.device.sensor_dto import SensorConfigDto
from services.application.application_service_protocol import ApplicationServiceProtocol
from station.station_protocol import StationProtocol
from web.events.app_events import EAppEvents
from web.events.station.station_update_event import StationUpdateEvent
from web.handlers.base_handler import BaseHandler


class SettingsHandler(BaseHandler):
    def __init__(self, dispatcher: EventDispatcherProtocol, socketio: SocketIO, station: StationProtocol, app_service: ApplicationServiceProtocol):
        super().__init__(dispatcher, socketio)
        self.__station = station
        self.__app_service = app_service

    @property
    def station(self) -> StationProtocol:
        return self.__station

    @property
    def app_service(self) -> ApplicationServiceProtocol:
        return self.__app_service

    def register(self):
        self.socketio.on_event(EAppEvents.SENSOR_SET_CONFIG, self.handle_sensor_set_config)
        self.socketio.on_event(EAppEvents.STATION_SET_CONFIG, self.handle_station_set_config)

    @BaseHandler.safe(error_message="Error setting sensor config.")
    def handle_sensor_set_config(self, data):
        config = SensorConfigDto.from_dict(data)
        self.station.set_sensor_config(config)
        return self.ok()

    @BaseHandler.safe(error_message="Error setting sensor config.")
    def handle_station_set_config(self, data):
        config = ApplicationDto(**data)
        self.app_service.update_config(config)
        return self.ok()