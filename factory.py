from typing import Sequence

from flask_socketio import SocketIO

from core.di.di_container import container
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from device.contactor.contactor_protocol import ContactorProtocol
from device.device_ids import EDeviceIds
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_mode import ESystemMode
from device.system.system_protocol import SystemProtocol
from dto.device.sensor_dto import SensorConfigDto
from services.application.application_service import ApplicationService
from services.application.application_service_protocol import ApplicationServiceProtocol
from web.handlers.station_handler import StationHandler


def read_number(prompt: str, number_type: type = float):
    """
    Reads a number (float or int) from the console.
    Keeps asking until valid input is provided.

    Args:
        prompt: Text to show to the user.
        number_type: Either float or int (default: float).

    Returns:
        The entered number converted to the requested type.
    """
    while True:
        try:
            return number_type(input(prompt))
        except ValueError:
            print(f"Invalid input! Please enter a valid {number_type.__name__}.")



def build_application_service(defaults = True) -> ApplicationServiceProtocol:
    system_count = 3 if defaults else read_number(f"Enter systems count:", int)
    set_point = 50.0 if defaults else read_number(f"Enter set point:", float)
    offset = 20.0 if defaults else read_number(f"Enter offset:", float)
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
    app_service = container.resolve(ApplicationServiceProtocol)

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
            ai_max=app_service.get_ai_max_raw(ai_id),
            ai_min=0,
            need_alarm_reset=False,
            alarm_start_delay=alarm_start_delay,
            alarm_stop_delay=alarm_stop_delay,
        ),
        ai_id=ai_id
    )
