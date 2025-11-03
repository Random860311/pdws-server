from web.events.station.station_update_event import StationUpdateEvent
from web.handlers.base_handler import BaseHandler


class StationHandler(BaseHandler):
    def register(self):
        self.dispatcher.subscribe(StationUpdateEvent, self.emit_event)