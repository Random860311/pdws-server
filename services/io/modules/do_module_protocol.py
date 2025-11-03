from typing import Protocol

from services.io.modules.digital_module_protocol import DigitalModuleProtocol



class DOModuleProtocol(DigitalModuleProtocol, Protocol):
    pass