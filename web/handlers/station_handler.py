from flask_socketio import SocketIO

from common import utils
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from device.system.system_mode import ESystemMode
from dto.string_dto import StringDto
from station.station_protocol import StationProtocol
from web.events.app_events import EAppEvents
from web.events.station.station_update_event import StationUpdateEvent
from web.handlers.base_handler import BaseHandler


class StationHandler(BaseHandler):
    def __init__(self, dispatcher: EventDispatcherProtocol, socketio: SocketIO, station: StationProtocol):
        super().__init__(dispatcher, socketio)
        self.__station = station

    @property
    def station(self) -> StationProtocol:
        return self.__station

    def register(self):
        self.socketio.on_event(EAppEvents.SYSTEM_SET_MODE, self.handle_system_set_mode)

        self.dispatcher.subscribe(StationUpdateEvent, self.emit_event)

    @BaseHandler.safe(error_message="Error setting system mode.")
    def handle_system_set_mode(self, data):
        print("Setting system mode: ", data)
        system_id = utils.get_int(data, "device_id")
        mode = utils.get_enum(data, "mode", ESystemMode)

        if system_id is None or mode is None:
            self.fail(StringDto("Invalid system id or mode."))

        self.station.set_system_mode(system_id, mode)
        return self.ok()