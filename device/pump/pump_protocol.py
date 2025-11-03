from typing import Protocol, runtime_checkable

from device.base.device_protocol import DeviceProtocol

@runtime_checkable
class PumpProtocol(DeviceProtocol, Protocol):
    pass