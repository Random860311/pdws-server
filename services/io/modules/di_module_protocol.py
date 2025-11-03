from typing import Protocol

from services.io.modules.digital_module_protocol import DigitalModuleProtocol



class DIModuleProtocol(DigitalModuleProtocol, Protocol):
    pass