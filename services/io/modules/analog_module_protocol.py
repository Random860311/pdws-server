from typing import Protocol, Optional

from services.io.modules.io_module_protocol import IOModuleProtocol


class AnalogModuleProtocol(IOModuleProtocol, Protocol):
    def get_value(self, pos: int) -> Optional[int]: ...

    def get_all_values(self) -> list[int]: ...

    def get_max_value(self) -> int: ...