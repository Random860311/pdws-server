from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from core.serializable_protocol import SerializableProtocol
from dto.base_dto import BaseDto


class EStatusCode(str, Enum):
    SUCCESS = "success",
    ERROR = "error"
    WARNING = "warning"

    @classmethod
    def from_value(cls, value: str, default: "EStatusCode" = None) -> "EStatusCode":
        try:
            return cls(value)
        except ValueError:
            print("Error: Invalid value for EStatusCode: ", value)
            if default is not None:
                return default
            raise

@dataclass
class ResponseDto(BaseDto):
    status_code: str
    data: Optional[SerializableProtocol] = field(kw_only=True, default=None)


