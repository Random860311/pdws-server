
from common import utils
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from device.sensor.sensor_alarm_manager import SensorAlarManager
from device.base.device import Device
from device.sensor.sensor_protocol import SensorProtocol
from dto.device.sensor_dto import SensorConfigDto, SensorDto
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.events.ai_event import AIEvent
from services.io.io_service_protocol import IOServiceProtocol

class Sensor(SensorProtocol, Device):
    def __init__(self, device_id: int, device_service: DeviceServiceProtocol, io_service: IOServiceProtocol, event_dispatcher: EventDispatcherProtocol, config: SensorConfigDto, ai_id: int):
        super().__init__(device_id, device_service, io_service, event_dispatcher)

        self.__config = device_service.get_sensor_config(device_id, self.device_name, config)
        self.__ai_id = ai_id
        self.__value_ai = 0

        self.__alarm_manager = SensorAlarManager(need_reset=config.need_alarm_reset)
        self.__alarm_manager.start_delay = config.alarm_start_delay
        self.__alarm_manager.stop_delay = config.alarm_stop_delay
        self.__alarm_manager.start_high = config.alarm_start_high
        self.__alarm_manager.stop_high = config.alarm_stop_high
        self.__alarm_manager.start_high_high = config.alarm_start_high_high
        self.__alarm_manager.stop_high_high = config.alarm_stop_high_high

        self.event_dispatcher.subscribe(AIEvent, self.__handle_ai_change)

    @property
    def device_name(self) -> str:
        return f"sensor_{self.device_id}"

    def __handle_ai_change(self, event: AIEvent):
        if event.io_id != self.ai_id:
            return
        # print(f"Sensor {self.device_name} AI change: {event}")
        self.ai = event.value_new

        # print(f"Sensor {self.device_name} Value: {self.value_scaled}")

    @property
    def value_scaled(self) -> float:
       return utils.scale_value(self.ai, self.ai_min, self.ai_max, self.value_scaled_max, self.value_scaled_min, clamp_output=True)

    @property
    def value_scaled_max(self) -> float:
        return self.__config.value_scaled_max

    @value_scaled_max.setter
    def value_scaled_max(self, value: float) -> None:
        self.__config.value_scaled_max = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def value_scaled_min(self) -> float:
        return self.__config.value_scaled_min

    @value_scaled_min.setter
    def value_scaled_min(self, value: float) -> None:
        self.__config.value_scaled_min = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def ai_id(self) -> int:
        return self.__ai_id

    @property
    def ai(self) -> int:
        return self.__value_ai

    @ai.setter
    def ai(self, value: int) -> None:
        self.__value_ai = value
        self.__alarm_manager.value = self.value_scaled
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def ai_max(self) -> int:
        return self.__config.ai_max

    @ai_max.setter
    def ai_max(self, value: int) -> None:
        self.__config.value_ai_max = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def ai_min(self) -> int:
        return self.__config.ai_min

    @ai_min.setter
    def ai_min(self, value: int) -> None:
        self.__config.value_ai_min = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def value_ma(self) -> float:
        return utils.scale_value(self.ai, self.ai_min, self.ai_max, 4, 20)

    @property
    def alarm_start_delay(self) -> float:
        return self.__alarm_manager.start_delay

    @alarm_start_delay.setter
    def alarm_start_delay(self, value: float) -> None:
        self.__alarm_manager.start_delay = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def alarm_stop_delay(self) -> float:
        return self.__alarm_manager.stop_delay

    @alarm_stop_delay.setter
    def alarm_stop_delay(self, value: float) -> None:
        self.__alarm_manager.stop_delay = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def alarm_start_high(self) -> float:
        return self.__alarm_manager.start_high

    @alarm_start_high.setter
    def alarm_start_high(self, value: float) -> None:
        self.__alarm_manager.start_high = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def alarm_stop_high(self) -> float:
        return self.__alarm_manager.stop_high

    @alarm_stop_high.setter
    def alarm_stop_high(self, value: float) -> None:
        self.__alarm_manager.stop_high = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def alarm_start_high_high(self) -> float:
        return self.__alarm_manager.start_high_high

    @alarm_start_high_high.setter
    def alarm_start_high_high(self, value: float) -> None:
        self.__alarm_manager.start_high_high = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def alarm_stop_high_high(self) -> float:
        return self.__alarm_manager.stop_high_high

    @alarm_stop_high_high.setter
    def alarm_stop_high_high(self, value: float) -> None:
        self.__alarm_manager.stop_high_high = value
        self.device_service.set_sensor_config(self.device_name, self.__config)

    @property
    def has_critical_alarm(self) -> bool:
        return super().has_critical_alarm or self.__alarm_manager.has_critical_alarm

    @property
    def has_alarm(self) -> bool:
        return super().has_alarm or self.__alarm_manager.has_alarm

    def reset(self) -> None:
        self.__alarm_manager.reset()

    def to_serializable(self) -> SerializableProtocol:
        return SensorDto(
            has_alarm=self.has_alarm,
            has_critical_alarm=self.has_critical_alarm,
            value_scaled=round(self.value_scaled, 1),
            value_ma=round(self.value_ma, 1),
            alarm_start_delay=int(self.alarm_start_delay),
            alarm_stop_delay=int(self.alarm_stop_delay),
            alarm_start_high=round(self.alarm_start_high, 1),
            alarm_stop_high=round(self.alarm_stop_high, 1),
            alarm_start_high_high=round(self.alarm_start_high_high, 1),
            alarm_stop_high_high=round(self.alarm_stop_high_high, 1),
            ai_max=self.ai_max,
            ai_min=self.ai_min,
            device_id=self.device_id,
            device_name=self.device_name,
            value_ai=self.ai,
            value_scaled_max=round(self.value_scaled_max, 1),
            value_scaled_min=round(self.value_scaled_min, 1),
            need_alarm_reset=False
        )
