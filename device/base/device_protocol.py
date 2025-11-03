from typing import Protocol

from common.alarm.alarm_protocol import AlarmProtocol
from core.serializable_protocol import SerializableProtocol


class DeviceProtocol(AlarmProtocol, Protocol):
    @property
    def device_id(self) -> int: ...

    @property
    def device_name(self) -> str: ...

    def to_serializable(self) -> SerializableProtocol: ...