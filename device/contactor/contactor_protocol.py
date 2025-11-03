from typing import Protocol, runtime_checkable

from device.base.device_runnable_protocol import DeviceRunnableProtocol


@runtime_checkable
class ContactorProtocol(DeviceRunnableProtocol, Protocol):
    pass