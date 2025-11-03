from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class StringDto(BaseDto):
    value: str