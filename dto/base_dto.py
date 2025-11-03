from datetime import date, datetime
from dataclasses import dataclass, is_dataclass, asdict, fields
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping


from core.serializable_protocol import SerializableProtocol

@dataclass
class BaseDto(SerializableProtocol):
    def to_dict(self) -> dict[str, Any]:
        return asdict(self) #_to_serializable(self)


def _to_serializable(obj: Any, _seen: set[int] | None = None) -> Any:
    if _seen is None:
        _seen = set()

    # primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # common conversions
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)  # or str(obj)
    if isinstance(obj, Enum):
        return obj.value   # or obj.name

    # dataclasses
    if is_dataclass(obj):
        oid = id(obj)
        if oid in _seen:
            return "<recursion>"
        _seen.add(oid)
        out: dict[str, Any] = {}
        for f in fields(obj):
            if f.metadata.get("serialize") is False:
                continue
            out[f.name] = _to_serializable(getattr(obj, f.name), _seen)
        _seen.remove(oid)
        return out

    # objects that expose to_dict per your protocol
    if isinstance(obj, SerializableProtocol):
        # Avoid calling our own to_dict and re-wrapping endlessly
        return obj.to_dict() if not is_dataclass(obj) else _to_serializable(obj, _seen)

    # containers
    if isinstance(obj, Mapping):
        return {str(k): _to_serializable(v, _seen) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_serializable(v, _seen) for v in obj]

    # last resort
    try:
        return str(obj)
    except Exception:
        return f"<unserializable {type(obj).__name__}>"