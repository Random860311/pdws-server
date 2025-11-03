from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.io.analog_io_dto import AnalogIoDto
from dto.io.digital_io_dto import DigitalIoDto


@dataclass
class IoStatusDto(BaseDto):
    di: list[DigitalIoDto]
    do: list[DigitalIoDto]
    ai: list[AnalogIoDto]
    ao: list[AnalogIoDto]