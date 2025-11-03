from dataclasses import dataclass

from dto.io.io_dto import IoDto


@dataclass
class DigitalIoDto(IoDto):
    value: bool