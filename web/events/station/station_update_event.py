from dto.station_dto import StationDto
from web.events.app_events import EAppEvents
from web.events.base_web_event import BaseWebEvent


class StationUpdateEvent(BaseWebEvent):
    def __init__(self, event: StationDto) -> None:
        super().__init__(EAppEvents.STATION_EMIT_UPDATE.value, event_data=event)