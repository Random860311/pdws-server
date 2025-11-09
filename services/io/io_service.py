import threading
from typing import Optional

from common import utils
from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from dto.io.analog_io_dto import AnalogIoDto
from dto.io.digital_io_dto import DigitalIoDto
from dto.io.io_status_dto import IoStatusDto
from services.io.events.ai_event import AIEvent
from services.io.events.di_event import DIEvent
from services.io.io_service_protocol import IOServiceProtocol
from services.io.modules.ai_module_protocol import AIModuleProtocol
from services.io.modules.ao_module_protocol import AOModuleProtocol
from services.io.modules.di_module_protocol import DIModuleProtocol
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

        self.__ai_modules = ai_modules if ai_modules else []
        self.__ao_modules = ao_modules if ao_modules else []
        self.__di_modules = di_modules if di_modules else []
        self.__do_modules = do_modules if do_modules else []

        self.__ai_lock = threading.RLock()
        self.__ao_lock = threading.RLock()
        self.__di_lock = threading.RLock()
        self.__do_lock = threading.RLock()

        for di_module in self.__di_modules:
            di_module.initialize()
            di_module.callback = self.__on_di_change

        for do_module in self.__do_modules:
            do_module.initialize()
            do_module.callback = self.__on_do_change

        for ai_module in self.__ai_modules:
            ai_module.initialize()

        for ao_module in self.__ao_modules:
            ao_module.initialize()

    def get_digital_input_value(self, di_pos: int) -> bool:
        with self.__di_lock:
            return self.__di_cache.get(di_pos, False)

    def get_digital_output_value(self, do_pos: int) -> bool:
        with self.__do_lock:
            return self.__do_cache.get(do_pos, False)

    def set_digital_output_value(self, do_pos: int, value: bool) -> None:
        print(f"Set DO: {do_pos}, Value: {value}")
        with self.__do_lock:
            module = next((m for m in self.__do_modules if m.managed_pos(do_pos)), None)
            if module:
                print("Module found, setting value")
                module.set_value(do_pos, value)

    def get_analog_input_value(self, ai_pos: int) -> int:
        with self.__ai_lock:
            return self.__ai_cache.get(ai_pos, 0)

    def get_analog_output_value(self, ao_pos: int) -> int:
        with self.__ao_lock:
            return self.__ao_cache.get(ao_pos, 0)

    def set_analog_output_value(self, ao_pos: int, value: int) -> None:
        pass

    def scan(self) -> None:
        with self.__ai_lock:
            ai_pos = 0
            for module in self.__ai_modules:
                for ai in module.get_all_values():
                    old_ai = self.__ai_cache.get(ai_pos)
                    if (old_ai is None) or (old_ai != ai):
                        # print(f"Sending event: AI: {ai_pos}, New: {ai}, Old: {old_ai}")
                        ai_event = AIEvent(io_id=ai_pos, value_old=old_ai, value_new=ai)
                        self.__ai_cache[ai_pos] = ai
                        self.__event_dispatcher.emit_async(ai_event)
                    ai_pos += 1

    def to_serializable(self) -> SerializableProtocol:
        with self.__di_lock:
            di = [DigitalIoDto(io_id=k, value=v) for k, v in self.__di_cache.items()]
        with self.__do_lock:
            do = [DigitalIoDto(io_id=k, value=v) for k, v in self.__do_cache.items()]
        with self.__ai_lock:
            ai: list[AnalogIoDto] = []
            ai_pos = 0
            for ai_module in self.__ai_modules:
                for ai_value in ai_module.get_all_values():
                    ai.append(AnalogIoDto(io_id=ai_pos, raw_value=ai_value, ma_value=utils.scale_value(ai_value, 0, ai_module.get_max_value(), 4, 20)))
                    ai_pos += 1
        with self.__ao_lock:
            ao: list[AnalogIoDto] = []
            ao_pos = 0
            for ao_module in self.__ao_modules:
                for ao_value in ao_module.get_all_values():
                    ao.append(AnalogIoDto(io_id=ao_pos, raw_value=ao_value, ma_value=utils.scale_value(ao_value, 0, ao_module.get_max_value(), 4, 20)))
                    ao_pos += 1

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
                self.__event_dispatcher.emit_async(DIEvent(io_id=do_pos, value_old=old_do, value_new=value))

    def get_ai_max_raw(self, ai_pos: int) -> int:
        with self.__ai_lock:
            module = next((m for m in self.__ai_modules if m.managed_pos(ai_pos)), None)
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

    @staticmethod
    def get_io_count(modules: list[IOModuleProtocol]) -> int:
        count = 0
        for m in modules:
            count += m.io_count
        return count