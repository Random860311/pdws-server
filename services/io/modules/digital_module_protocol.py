from typing import Protocol, Optional, Callable, Tuple

from services.io.modules.io_module_protocol import IOModuleProtocol


class DigitalModuleProtocol(IOModuleProtocol, Protocol):
    def get_value(self, di_pos: int) -> Optional[bool]: ...

    def get_all_values(self) -> list[bool]: ...

    @property
    def callback(self) -> Optional[Callable[[int, bool], None]]: ...

    @callback.setter
    def callback(self, value: Optional[Callable[[int, bool], None]]) -> None: ...