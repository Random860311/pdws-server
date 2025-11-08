from enum import Enum
from typing import Tuple, Optional, TypeVar, Type, Any

TEnum = TypeVar("TEnum", bound=Enum)

def scale_value(
    in_value: float,
    in_value_min: float,
    in_value_max: float,
    out_value_min: float,
    out_value_max: float,
    *,
    clamp_output: bool = True,
    offset: float = 0.0
) -> float:
    """
    Scales `in_value` from [in_value_min, in_value_max] to [out_value_min, out_value_max],
    then adds `offset`. Optionally clamps the *final* result to the output range.

    Args:
        in_value (float): The input value to scale.
        in_value_min (float): Minimum of the input range.
        in_value_max (float): Maximum of the input range.
        out_value_min (float): Minimum of the output range.
        out_value_max (float): Maximum of the output range.
        clamp_output (bool, optional): If True, clamp the final result to the output range.
        offset (float, optional): Value added to the scaled result at the end.

    Returns:
        float: The scaled (and possibly clamped) value plus offset.
    """
    if in_value_max == in_value_min:
        return 0

    # Normalize input to 0–1 (works for ascending or descending input ranges)
    normalized = (in_value - in_value_min) / (in_value_max - in_value_min)

    # Scale to output range (works for ascending or descending output ranges)
    scaled = out_value_min + normalized * (out_value_max - out_value_min)

    if clamp_output:
        lo = min(out_value_min, out_value_max)
        hi = max(out_value_min, out_value_max)
        if scaled < lo:
            return lo + offset
        if scaled > hi:
            return hi + offset

    return scaled + offset

def split_elapsed(seconds: float) -> Tuple[int, int, int, int]:
    """
    Convert non-negative seconds into (days, hours, minutes, seconds).

    Args:
        seconds: Elapsed time in seconds (must be >= 0).

    Returns:
        (days, hours, minutes, seconds) where seconds may be fractional.
    """
    if seconds < 0:
        return 0,0,0,0

    days, rem = divmod(seconds, 86400)   # 24 * 60 * 60
    hours, rem = divmod(rem, 3600)       # 60 * 60
    minutes, secs = divmod(rem, 60)

    return int(days), int(hours), int(minutes), int(secs)

def get_int(data: dict, key: str, default: Optional[int] = None) -> int:
    """Parse an int field or raise ValueError"""
    try:
        return int(data.get(key, default))
    except Exception:
        raise ValueError(f"Missing or invalid '{key}'.")

def get_bool(data: dict, key: str, default: Optional[bool] = None) -> bool:
    """Parse a bool field or raise ValueError"""
    try:
        return bool(data.get(key, default))
    except Exception:
        raise ValueError(f"Missing or invalid '{key}'.")

def get_enum(data: dict, key: str, enum_cls: Type[TEnum], default: Optional[TEnum] = None)-> TEnum:
    value = data.get(key)
    if value is None:
        return default
    return enum_from_any(enum_cls, value, default)

def enum_from_any(enum_cls: Type[TEnum], value: Any, default: Optional[TEnum] = None) -> TEnum:
    try:
        # Try by value first
        return enum_cls(value)
    except (ValueError, TypeError):
        if isinstance(value, str):
            try:
                return enum_cls[value]  # lookup by NAME (exact case)
            except KeyError:
                pass
        if default is not None:
            return default
        raise ValueError(f"{value!r} is not a valid {enum_cls.__name__}")
