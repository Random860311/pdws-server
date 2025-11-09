from flask import Flask
from flask_socketio import SocketIO

from core.di.di_container import container
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.thread_manager_protocol import ThreadManagerProtocol
from device.contactor.contactor import Contactor
from device.contactor.contactor_protocol import ContactorProtocol
from device.pump.pump import Pump
from device.pump.pump_protocol import PumpProtocol
from device.sensor.sensor import Sensor
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system import System
from device.system.system_protocol import SystemProtocol
from factory import build_application_systems, build_pressure_sensor, build_application_service, build_thread_manager, build_event_dispatcher, build_io_service
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.device.device_service import DeviceService
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.io_service_protocol import IOServiceProtocol
from station.alternatator.alternator_protocol import AlternatorProtocol
from station.alternatator.time_alternator import TimeAlternator
from station.starter.incremental_basic_starter import IncBasicStarter
from station.station import Station
from station.station_protocol import StationProtocol
from web.handlers.station_handler import StationHandler
from web.socket_app import socketio, flask_app

def create_di(defaults=True) -> StationProtocol:
    container.register_instance(SocketIO, socketio)
    container.register_instance(Flask, flask_app)
    container.register_instance(ThreadManagerProtocol, build_thread_manager())
    container.register_instance(EventDispatcherProtocol, build_event_dispatcher())

    container.register_instance(IOServiceProtocol, build_io_service())
    container.register_instance(ApplicationServiceProtocol, build_application_service(defaults=defaults))
    container.register_instance(DeviceServiceProtocol, DeviceService())

    container.register_factory(
        SensorProtocol,
        lambda *args, **kwargs: Sensor(
            *args,
            **{
                **kwargs,
                "device_service": container.resolve(DeviceServiceProtocol),
                "io_service": container.resolve(IOServiceProtocol),
                "event_dispatcher": container.resolve(EventDispatcherProtocol)
            }
        )
    )
    container.register_factory(
        ContactorProtocol,
        lambda *args, **kwargs: Contactor(
            *args,
            **{
                **kwargs,
                "device_service": container.resolve(DeviceServiceProtocol),
                "io_service": container.resolve(IOServiceProtocol),
                "event_dispatcher": container.resolve(EventDispatcherProtocol)
            }
        )
    )
    container.register_factory(
        PumpProtocol,
        lambda *args, **kwargs: Pump(
            *args,
            **{
                **kwargs,
                "device_service": container.resolve(DeviceServiceProtocol),
                "io_service": container.resolve(IOServiceProtocol),
                "event_dispatcher": container.resolve(EventDispatcherProtocol)
            }
        )
    )
    container.register_factory(
        SystemProtocol,
        lambda *args, **kwargs: System(
            *args,
            **{
                **kwargs,
                "device_service": container.resolve(DeviceServiceProtocol),
                "io_service": container.resolve(IOServiceProtocol),
                "event_dispatcher": container.resolve(EventDispatcherProtocol)
            }
        )
    )

    systems = build_application_systems(defaults=defaults)
    pressure_sensor = build_pressure_sensor(defaults=defaults)

    container.register_instance(AlternatorProtocol, TimeAlternator(systems=systems))

    starter = IncBasicStarter(
        app_service=container.resolve(ApplicationServiceProtocol),
        sensor=pressure_sensor,
        systems=systems
    )

    station = Station(
        thread_manager=container.resolve(ThreadManagerProtocol),
        event_dispatcher=container.resolve(EventDispatcherProtocol),
        alternator=container.resolve(AlternatorProtocol),
        io_service=container.resolve(IOServiceProtocol),
        app_service=container.resolve(ApplicationServiceProtocol),
        starter=starter,
        sensor_pressure = pressure_sensor,
        systems=systems,
    )

    #region Web Handlers
    container.register_instance(StationProtocol, station)

    station_handler = StationHandler(
        socketio=socketio,
        dispatcher=container.resolve(EventDispatcherProtocol),
        station=container.resolve(StationProtocol)
    )

    station_handler.register()

    container.register_instance(StationHandler, station_handler)
    #endregion

    return station


