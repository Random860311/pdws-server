from core.serializable_protocol import SerializableProtocol
from device.base.device import Device
from device.pump.pump_protocol import PumpProtocol
from dto.device.pump_dto import PumpDto


class Pump(PumpProtocol, Device):
    def __init__(self, device_id: int):
        super().__init__(device_id)

    @property
    def device_name(self) -> str:
        return f"pump_{self.device_id}"

    def to_serializable(self) -> SerializableProtocol:
        return PumpDto(
            device_id=self.device_id,
            device_name=self.device_name,
            has_alarm=self.has_alarm,
            has_critical_alarm=self.has_critical_alarm,
        )