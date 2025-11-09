from typing import Sequence

import pigpio
from flask_socketio import SocketIO

from common.utils import read_number
from core.di.di_container import container
from core.dispatcher.event_dispatcher import EventDispatcher
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.thread_manager_protocol import ThreadManagerProtocol, ThreadManager
from device.contactor.contactor_protocol import ContactorProtocol
from device.device_ids import EDeviceIds
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_mode import ESystemMode
from device.system.system_protocol import SystemProtocol
from dto.device.sensor_dto import SensorConfigDto
from services.application.application_service import ApplicationService
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.io.io_service import IOService
from services.io.io_service_protocol import IOServiceProtocol
from services.io.modules.ads1x.ads1115_ai import Ads1115_AI
from services.io.modules.gpio.gpio_di import GPIO_DI
from services.io.modules.gpio.gpio_do import GPIO_DO


def build_io_service() -> IOServiceProtocol:
    pi = pigpio.pi()

    ai_module_0 = Ads1115_AI()
    di_module_0 = GPIO_DI(pi)
    do_module_0 = GPIO_DO(pi)

    io_service = IOService(
        event_dispatcher=container.resolve(EventDispatcherProtocol),
        ai_modules=[ai_module_0],
        di_modules=[di_module_0],
        do_modules=[do_module_0]
    )

    return io_service

def build_event_dispatcher() -> EventDispatcherProtocol:
    return EventDispatcher(thread_manager=container.resolve(ThreadManagerProtocol))

def build_thread_manager() -> ThreadManagerProtocol:
    return ThreadManager(socketio=container.resolve(SocketIO))

def build_application_service(defaults = True) -> ApplicationServiceProtocol:
    system_count = 3 if defaults else read_number(f"Enter systems count:", int)
    set_point = 50.0 if defaults else read_number(f"Enter set point:", float)
    offset = 5.0 if defaults else read_number(f"Enter offset:", float)
    start_pump_delay = 5 if defaults else read_number(f"Enter start pumps delay (s):", int)
    stop_pump_delay = 5 if defaults else read_number(f"Enter stop pumps delay (s):", int)


    application_service = ApplicationService(
        system_count=system_count,
        level_set_point=set_point,
        level_offset=offset,
        start_pump_delay=start_pump_delay,
        stop_pump_delay=stop_pump_delay
    )

    return application_service

def build_contactor_list(defaults = True) -> Sequence[ContactorProtocol]:
    app_service = container.resolve(ApplicationServiceProtocol)
    contactor_list = []
    for i in range(0, app_service.system_count):
        contactor_list.append(
            container.resolve_new(
                ContactorProtocol,
                device_id=i + 1,
                di_running=i if defaults else read_number(f"Enter digital input number for RUNNING of contactor {i + 1}:", int),
                do_run=i if defaults else read_number(f"Enter digital output number for RUN CMD of contactor {i + 1}:", int)
            )
        )
    return contactor_list

def build_application_systems(defaults = True) -> Sequence[SystemProtocol]:
    app_service = container.resolve(ApplicationServiceProtocol)

    contactor_list = build_contactor_list(defaults=defaults)
    systems_list = []

    position_hand = app_service.system_count
    position_auto = position_hand + 1

    for i in range(0, app_service.system_count):
        systems_list.append(
            container.resolve_new(
                SystemProtocol,
                device_id=i+1,
                contactor=contactor_list[i],
                pump=None,
                mode=ESystemMode.OFF,
                di_hand=position_hand if defaults else read_number(f"Enter digital input number for HAND of system {i + 1}:", int),
                di_auto=position_auto if defaults else read_number(f"Enter digital input number for AUTO of system {i + 1}:", int),
            )
        )
        position_hand = position_auto + 1
        position_auto = position_hand + 1
    return systems_list

def build_pressure_sensor(defaults = True) -> SensorProtocol:
    io_service = container.resolve(IOServiceProtocol)

    value_scaled_max = 100.0 if defaults else read_number(f"Enter pressure sensor ENG MAX VALUE:", float)
    value_scaled_min = 0.0 if defaults else read_number(f"Enter pressure sensor ENG MIN VALUE:", float)
    ai_id = 0 if defaults else read_number(f"Enter analog input number:", int)
    alarm_start_delay = 5 if defaults else read_number(f"Enter alarm start delay in (s):", int)
    alarm_stop_delay = 5 if defaults else read_number(f"Enter alarm stop delay in (s):", int)

    return container.resolve_new(
        SensorProtocol,
        device_id=EDeviceIds.SENSOR_PRESSURE,
        config=SensorConfigDto(
            device_id=EDeviceIds.SENSOR_PRESSURE,
            value_scaled_max=value_scaled_max,
            value_scaled_min=value_scaled_min,
            ai_max=io_service.get_ai_max_raw(ai_id),
            ai_min=0,
            need_alarm_reset=False,
            alarm_start_delay=alarm_start_delay,
            alarm_stop_delay=alarm_stop_delay,

            alarm_start_high_high=value_scaled_max * 0.9,
            alarm_stop_high_high=value_scaled_max * 0.85,
            alarm_start_high=value_scaled_max * 0.8,
            alarm_stop_high=value_scaled_max * 0.75,
            alarm_start_low=value_scaled_max * 0.15,
            alarm_stop_low=value_scaled_max * 0.20,
            alarm_start_low_low=value_scaled_max * 0.05,
            alarm_stop_low_low=value_scaled_max * 0.1,
        ),
        ai_id=ai_id
    )
