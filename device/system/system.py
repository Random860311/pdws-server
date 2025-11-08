from typing import TypedDict, Optional, Unpack

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from device.base.device import Device
from device.base.device_status import EDeviceStatus
from device.contactor.contactor_protocol import ContactorProtocol
from device.pump.pump_protocol import PumpProtocol
from device.system.system_mode import ESystemMode
from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol
from dto.device.system_dto import SystemDto
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.events.di_event import DIEvent
from services.io.io_service_protocol import IOServiceProtocol

class SystemKwargs(TypedDict, total=False):
    contactor: Optional[ContactorProtocol]
    pump: Optional[PumpProtocol]
    mode: ESystemMode
    di_hand: int
    di_auto: int

class System(SystemProtocol, Device):
    def __init__(
            self,
            device_id: int,
            device_service: DeviceServiceProtocol,
            io_service: IOServiceProtocol,
            event_dispatcher: EventDispatcherProtocol,
            **kwargs: Unpack[SystemKwargs]
    ):
        super().__init__(device_id, device_service, io_service, event_dispatcher)

        self.__args = kwargs

        self.__di_hand = kwargs.get("di_hand", 0)
        self.__di_auto = kwargs.get("di_auto", 0)

        self.__priority_hand = ESystemPriority.OUT
        self.__priority_auto = ESystemPriority.OUT

        self.__software_mode = kwargs.get("mode", ESystemMode.OFF)
        self.__physical_mode: ESystemMode = ESystemMode.OFF

        event_dispatcher.subscribe(DIEvent, self.__handle_di_change)

    def __handle_di_change(self, event: DIEvent):
        if not event.io_id in [self.__di_auto, self.__di_hand]:
            return
        if event.io_id == self.__di_hand and event.value_new:
            self.__physical_mode = ESystemMode.HAND
        elif event.io_id == self.__di_auto and event.value_new:
            self.__physical_mode = ESystemMode.AUTO
        else:
            self.__physical_mode = ESystemMode.OFF

    def __update_mode(self):
        if self.mode == ESystemMode.OFF:
            self.stop()
        elif self.mode == ESystemMode.HAND:
            self.call_to_run()
        # Do not start if auto, wait for alternator order

    @property
    def device_name(self) -> str:
        return f"system_{self.device_id}"

    @property
    def status(self) -> EDeviceStatus:
        return self.contactor.status if self.contactor is not None else EDeviceStatus.STOPPED

    @status.setter
    def status(self, value: EDeviceStatus) -> None:
        if self.contactor is not None:
            self.contactor.status = value

    @property
    def can_run(self) -> bool:
        return (self.mode != ESystemMode.OFF) and (not self.has_critical_alarm) and (self.contactor.can_run if self.contactor else False)

    @property
    def can_run_auto(self) -> bool:
        return self.can_run and (self.mode == ESystemMode.AUTO) and (self.contactor.can_run_auto if self.contactor else False)

    def call_to_run(self) -> None:
        if (self.mode == ESystemMode.AUTO and self.can_run_auto) or (self.mode == ESystemMode.HAND and self.can_run):
            self.contactor.call_to_run()

    def stop(self) -> None:
        if self.contactor is not None:
            self.contactor.stop()

    def set_emergency_stop(self, value: bool) -> None:
        if self.contactor is not None:
            self.contactor.set_emergency_stop(value)

    @property
    def alarm_fail_to_start_delay(self) -> int:
        return self.contactor.alarm_fail_to_start_delay if self.contactor is not None else 0

    @alarm_fail_to_start_delay.setter
    def alarm_fail_to_start_delay(self, value: int) -> None:
        if self.contactor is not None:
            self.contactor.alarm_fail_to_start_delay = value

    @property
    def alarm_fail_to_start(self) -> bool:
        return self.contactor.alarm_fail_to_start if self.contactor is not None else False

    @property
    def has_critical_alarm(self) -> bool:
        result = False
        if self.contactor is not None:
            result = self.contactor.has_critical_alarm
        if self.pump is not None:
            result = result or self.pump.has_critical_alarm
        return result

    @property
    def has_alarm(self) -> bool:
        result = False
        if self.contactor is not None:
            result = self.contactor.has_alarm
        if self.pump is not None:
            result = result or self.pump.has_alarm
        return result

    @property
    def run_time_current(self) -> float:
        return self.contactor.run_time_current if self.contactor is not None else 0

    @property
    def run_time_last(self) -> float:
        return self.contactor.run_time_last if self.contactor is not None else 0

    @property
    def run_time_total(self) -> float:
        return self.contactor.run_time_total if self.contactor is not None else 0

    def reset_run_time(self) -> None:
        if self.contactor is not None:
            self.contactor.reset_run_time()

    @property
    def contactor(self) -> Optional[ContactorProtocol]:
        return self.__args.get("contactor")

    @property
    def pump(self) -> Optional[PumpProtocol]:
        return self.__args.get("pump")

    @property
    def mode(self) -> ESystemMode:
        # if self.__physical_mode == ESystemMode.OFF:
        #     return ESystemMode.OFF
        # elif self.__physical_mode == ESystemMode.HAND:
        #     return ESystemMode.HAND
        return self.__software_mode

    @mode.setter
    def mode(self, value: ESystemMode) -> None:
        self.__software_mode = value
        self.__update_mode()

    @property
    def priority(self) -> ESystemPriority:
        if self.can_run_auto:
            return self.priority_auto
        elif self.can_run:
            return self.priority_hand

        return ESystemPriority.OUT

    @property
    def priority_auto(self) -> ESystemPriority:
        return self.__priority_auto if self.can_run_auto else ESystemPriority.OUT

    @priority_auto.setter
    def priority_auto(self, value: ESystemPriority) -> None:
        self.__priority_auto = value

    @property
    def priority_hand(self) -> ESystemPriority:
        return self.__priority_hand if self.can_run else ESystemPriority.OUT

    @property
    def is_called_to_run(self) -> bool:
        return self.contactor.is_called_to_run if self.contactor else False

    @priority_hand.setter
    def priority_hand(self, value: ESystemPriority) -> None:
        self.__priority_hand = value

    def to_serializable(self) -> SerializableProtocol:
        contactor_dto = self.contactor.to_serializable() if self.contactor is not None else None
        pump_dto = self.pump.to_serializable() if self.pump is not None else None

        return SystemDto(
            device_id=self.device_id,
            device_name=self.device_name,
            has_critical_alarm=self.has_critical_alarm,
            has_alarm=self.has_alarm,

            status=self.status,
            can_run=self.can_run,
            can_run_auto=self.can_run_auto,
            call_to_run=self.is_called_to_run,
            alarm_fail_to_start=self.alarm_fail_to_start,

            mode=self.mode,
            priority=self.priority,
            priority_hand=self.priority_hand,
            priority_auto=self.priority_auto,
            contactor=contactor_dto,
            pump=pump_dto,
        )

