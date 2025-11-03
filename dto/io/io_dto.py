from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class IoDto(BaseDto):
    io_id: int