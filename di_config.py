import pigpio
from flask import Flask
from flask_socketio import SocketIO

from core.di.di_container import container
from core.dispatcher.event_dispatcher import EventDispatcher
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.thread_manager_protocol import ThreadManager, ThreadManagerProtocol
from device.contactor.contactor import Contactor
from device.contactor.contactor_protocol import ContactorProtocol
from device.pump.pump import Pump
from device.pump.pump_protocol import PumpProtocol
from device.sensor.sensor import Sensor
from device.sensor.sensor_protocol import SensorProtocol
from device.system.system import System
from device.system.system_protocol import SystemProtocol
from factory import build_application_systems, build_pressure_sensor, build_application_service
from services.application.application_service_protocol import ApplicationServiceProtocol
from services.device.device_service import DeviceService
from services.device.device_service_protocol import DeviceServiceProtocol
from services.io.io_service import IOService
from services.io.io_service_protocol import IOServiceProtocol
from services.io.modules.ads1x.ads1115_ai import Ads1115_AI
from services.io.modules.gpio.gpio_di import GPIO_DI
from station.alternatator.alternator_protocol import AlternatorProtocol
from station.alternatator.time_alternator import TimeAlternator
from station.starter.IncBasicStarter import IncBasicStarter
from station.station import Station
from station.station_protocol import StationProtocol
from web.handlers.station_handler import StationHandler
from web.socket_app import socketio, flask_app

def create_di(defaults=True) -> StationProtocol:
    #region SocketIO and Flask

    container.register_instance(SocketIO, socketio)
    container.register_instance(Flask, flask_app)

    #endregion

    #region ThreadManager

    thread_manager = ThreadManager(socketio=socketio)
    container.register_instance(ThreadManagerProtocol, thread_manager)

    #endregion

    #region EventDispatcher

    event_dispatcher = EventDispatcher(thread_manager=thread_manager)
    container.register_instance(EventDispatcherProtocol, event_dispatcher)

    #endregion

    #region Services

    device_service = DeviceService()

    ai_module_0 = Ads1115_AI()
    di_module_0 = GPIO_DI(pigpio.pi())

    application_service = build_application_service(defaults=defaults)

    for i in range(0, ai_module_0.io_count):
        application_service.set_ai_max_raw(i, ai_module_0.get_max_value())

    io_service = IOService(
        event_dispatcher=event_dispatcher,
        ai_modules=[ai_module_0],
        di_modules=[di_module_0]
    )

    container.register_instance(IOServiceProtocol, io_service)
    container.register_instance(ApplicationServiceProtocol, application_service)
    container.register_instance(DeviceServiceProtocol, device_service)

    #endregion

    #region Devices

    container.register_factory(
        SensorProtocol,
        lambda *args, **kwargs: Sensor(
            *args,
            **{
                **kwargs,
                "device_service": device_service,
                "io_service": io_service,
                "event_dispatcher": event_dispatcher
            }
        )
    )

    container.register_factory(
        ContactorProtocol,
        lambda *args, **kwargs: Contactor(
            *args,
            **{
                **kwargs,
                "device_service": device_service,
                "io_service": io_service,
                "event_dispatcher": event_dispatcher
            }
        )
    )

    container.register_factory(
        PumpProtocol,
        lambda *args, **kwargs: Pump(
            *args,
            **{
                **kwargs,
                "device_service": device_service,
                "io_service": io_service,
                "event_dispatcher": event_dispatcher
            }
        )
    )

    container.register_factory(
        SystemProtocol,
        lambda *args, **kwargs: System(
            *args,
            **{
                **kwargs,
                "device_service": device_service,
                "io_service": io_service,
                "event_dispatcher": event_dispatcher
            }
        )
    )

    #endregion

    systems = build_application_systems(defaults=defaults)

    alternator = TimeAlternator(systems=systems)
    container.register_instance(AlternatorProtocol, alternator)

    pressure_sensor = build_pressure_sensor(defaults=defaults)

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
        starter=starter,
        sensor_pressure = pressure_sensor,
        systems=systems,
    )

    #region Web Handlers
    container.register_instance(StationProtocol, station)

    station_handler = StationHandler(socketio=socketio, dispatcher=container.resolve(EventDispatcherProtocol))

    station_handler.register()

    container.register_instance(StationHandler, station_handler)
    #endregion

    return station


