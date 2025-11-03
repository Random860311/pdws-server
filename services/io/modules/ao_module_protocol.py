from typing import Protocol, Optional

from services.io.modules.analog_module_protocol import AnalogModuleProtocol


class AOModuleProtocol(AnalogModuleProtocol, Protocol):
    pass