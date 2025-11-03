from dataclasses import dataclass, field


from dto.io.io_dto import IoDto


@dataclass
class AnalogIoDto(IoDto):
    raw_value: int
    ma_value: float = field(kw_only=True, compare=False, default=0.0)