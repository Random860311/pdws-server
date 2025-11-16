import threading
from typing import Optional, Callable

from common import utils
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from dto.io.analog_io_dto import AnalogIoDto
from dto.io.digital_io_dto import DigitalIoDto
from dto.io.io_status_dto import IoStatusDto
from services.io.events.ai_event import AIEvent
from services.io.events.ao_event import AOEvent
from services.io.events.di_event import DIEvent
from services.io.events.do_event import DOEvent
from services.io.io_service_protocol import IOServiceProtocol
from services.io.modules.ai_module_protocol import AIModuleProtocol
from services.io.modules.analog_module_protocol import AnalogModuleProtocol
from services.io.modules.ao_module_protocol import AOModuleProtocol
from services.io.modules.di_module_protocol import DIModuleProtocol
from services.io.modules.digital_module_protocol import DigitalModuleProtocol
from services.io.modules.do_module_protocol import DOModuleProtocol
from services.io.modules.io_module_protocol import IOModuleProtocol


class IOService(IOServiceProtocol):
    def __init__(
            self,
            event_dispatcher: EventDispatcherProtocol,
            ai_modules: Optional[list[AIModuleProtocol]] = None,
            ao_modules: Optional[list[AOModuleProtocol]] = None,
            di_modules: Optional[list[DIModuleProtocol]] = None,
            do_modules: Optional[list[DOModuleProtocol]] = None
    ):
        self.__event_dispatcher = event_dispatcher
        self.__di_cache: dict[int, bool] = {}
        self.__do_cache: dict[int, bool] = {}
        self.__ai_cache: dict[int, int] = {}
        self.__ao_cache: dict[int, int] = {}

        self.__ai_modules: list[AIModuleProtocol] = ai_modules if ai_modules else []
        self.__ao_modules: list[AOModuleProtocol] = ao_modules if ao_modules else []
        self.__di_modules: list[DIModuleProtocol] = di_modules if di_modules else []
        self.__do_modules: list[DOModuleProtocol] = do_modules if do_modules else []

        self.__ai_lock = threading.RLock()
        self.__ao_lock = threading.RLock()
        self.__di_lock = threading.RLock()
        self.__do_lock = threading.RLock()

        self.init_digital_modules(self.__di_modules, self.__on_di_change)
        self.init_digital_modules(self.__do_modules, self.__on_do_change)

        self.init_analog_modules(self.__ai_modules)
        self.init_analog_modules(self.__ao_modules)

    @staticmethod
    def init_digital_modules(modules: list[DigitalModuleProtocol], callback: Optional[Callable[[int, bool|bool], None]] = None) -> None:
        for module in modules:
            module.initialize()
            module.callback = callback

    @staticmethod
    def init_analog_modules(modules: list[AIModuleProtocol]) -> None:
        for module in modules:
            module.initialize()

    def get_digital_input_value(self, pos: int) -> bool:
        with self.__di_lock:
            return self.__di_cache.get(pos, False)

    def get_digital_output_value(self, pos: int) -> bool:
        with self.__do_lock:
            return self.__do_cache.get(pos, False)

    def get_analog_input_value(self, pos: int) -> int:
        with self.__ai_lock:
            return self.__ai_cache.get(pos, 0)

    def get_analog_output_value(self, pos: int) -> int:
        with self.__ao_lock:
            return self.__ao_cache.get(pos, 0)

    def set_digital_output_value(self, pos: int, value: bool) -> None:
        with self.__do_lock:
            module = next((m for m in self.__do_modules if m.is_managed_pos(pos)), None)
            if module:
                module.set_value(pos, value)

    def set_analog_output_value(self, ao_pos: int, value: int) -> None:
        pass

    @staticmethod
    def scan_channel(modules: list[IOModuleProtocol], cache: dict[int, bool | int], event_cls, dispatcher: EventDispatcherProtocol, lock: threading.RLock) -> None:
        with lock:
            pos = 0
            for module in modules:
                for value in module.get_all_values():
                    old = cache.get(pos)
                    if old != value:  # covers old is None or different
                        cache[pos] = value
                        dispatcher.emit_async(event_cls(io_id=pos, value_old=old, value_new=value))
                    pos += 1

    def scan(self) -> None:
        self.scan_channel(self.__di_modules, self.__di_cache, DIEvent, self.__event_dispatcher, self.__di_lock)
        self.scan_channel(self.__do_modules, self.__do_cache, DOEvent, self.__event_dispatcher, self.__do_lock)
        self.scan_channel(self.__ai_modules, self.__ai_cache, AIEvent, self.__event_dispatcher, self.__ai_lock)
        self.scan_channel(self.__ao_modules, self.__ao_cache, AOEvent, self.__event_dispatcher, self.__ao_lock)

    @staticmethod
    def serialize_digital_modules(modules: list[DigitalModuleProtocol], lock: threading.RLock) -> list[DigitalIoDto]:
        with lock:
            result: list[DigitalIoDto] = []
            pos = 0
            for module in modules:
                for value in module.get_all_values():
                    result.append(DigitalIoDto(io_id=pos, value=value))
                    pos += 1
            return result

    @staticmethod
    def serialize_analog_modules(modules: list[AnalogModuleProtocol], lock: threading.RLock) -> list[AnalogIoDto]:
        with lock:
            result: list[AnalogIoDto] = []
            pos = 0
            for module in modules:
                for value in module.get_all_values():
                    result.append(AnalogIoDto(io_id=pos, raw_value=value, ma_value=round(utils.scale_value(value, 0, module.get_max_value(), 4, 20), 1)))
                    pos += 1
            return result

    def to_serializable(self) -> SerializableProtocol:
        di = self.serialize_digital_modules(self.__di_modules, self.__di_lock)
        do = self.serialize_digital_modules(self.__do_modules, self.__do_lock)
        ai = self.serialize_analog_modules(self.__ai_modules, self.__ai_lock)
        ao = self.serialize_analog_modules(self.__ao_modules, self.__ao_lock)

        return IoStatusDto(di=di, do=do, ai=ai, ao=ao)

    def __on_di_change(self, di_pos: int, value: bool) -> None:
        with self.__di_lock:
            old_di = self.__di_cache.get(di_pos)
            if (old_di is None) or (old_di != value):
                self.__di_cache[di_pos] = value
                self.__event_dispatcher.emit_async(DIEvent(io_id=di_pos, value_old=old_di, value_new=value))

    def __on_do_change(self, do_pos: int, value: bool) -> None:
        with self.__do_lock:
            old_do = self.__do_cache.get(do_pos)
            if (old_do is None) or (old_do != value):
                self.__do_cache[do_pos] = value
                self.__event_dispatcher.emit_async(DOEvent(io_id=do_pos, value_old=old_do, value_new=value))

    def get_ai_max_raw(self, ai_pos: int) -> int:
        with self.__ai_lock:
            module = next((m for m in self.__ai_modules if m.is_managed_pos(ai_pos)), None)
            return module.get_max_value() if module else 0

    def get_ao_max_raw(self, ao_pos: int) -> int:
        return 0

    def get_ai_count(self) -> int:
        with self.__ai_lock:
            return self.get_io_count(self.__ai_modules)

    def get_di_count(self) -> int:
        with self.__di_lock:
            return self.get_io_count(self.__di_modules)

    def get_ao_count(self) -> int:
        with self.__ao_lock:
            return self.get_io_count(self.__ao_modules)

    def get_do_count(self) -> int:
        with self.__do_lock:
            return self.get_io_count(self.__do_modules)

    @property
    def di_emergency_stop(self) -> int:
        return 9

    @staticmethod
    def get_io_count(modules: list[IOModuleProtocol]) -> int:
        count = 0
        for m in modules:
            count += m.io_count
        return count