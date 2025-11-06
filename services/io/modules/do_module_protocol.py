from typing import Protocol

from services.io.modules.digital_module_protocol import DigitalModuleProtocol



class DOModuleProtocol(DigitalModuleProtocol, Protocol):
    def set_value(self, do_pos: int, value: bool) -> None: ...