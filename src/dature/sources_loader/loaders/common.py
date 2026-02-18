import json
from datetime import date, datetime, time

# Expected number of time parts in HH:MM:SS format
TIME_PARTS_WITH_SECONDS = 3

# Expected number of time parts in HH:MM format
TIME_PARTS_WITHOUT_SECONDS = 2


def date_from_string(value: str) -> date:
    return date.fromisoformat(value)


def datetime_from_string(value: str) -> datetime:
    return datetime.fromisoformat(value)


def time_from_string(value: str) -> time:
    parts = value.split(":")
    if len(parts) == TIME_PARTS_WITH_SECONDS:
        return time(int(parts[0]), int(parts[1]), int(parts[2]))
    if len(parts) == TIME_PARTS_WITHOUT_SECONDS:
        return time(int(parts[0]), int(parts[1]))
    msg = f"Invalid time format: {value}"
    raise ValueError(msg)


def date_passthrough(value: date) -> date:
    return value


def datetime_passthrough(value: datetime) -> datetime:
    return value


def bytearray_from_string(value: str) -> bytearray:
    return bytearray(value, "utf-8")


def none_from_empty_string(value: str) -> None:
    if value == "":
        return
    msg = f"Cannot convert {value!r} to None"
    raise TypeError(msg)


def optional_from_empty_string(value: str) -> str | None:
    if value == "":
        return None
    return value


def _bool_from_string(value: str) -> bool:
    lower = value.lower().strip()
    if lower in ("true", "1", "yes", "on"):
        return True
    if lower in ("false", "0", "no", "off", ""):
        return False
    msg = f"Cannot convert {value!r} to bool"
    raise TypeError(msg)


def bool_loader(value: str | bool) -> bool:  # noqa: FBT001
    if isinstance(value, bool):
        return value
    return _bool_from_string(value)


def bytearray_from_json_string(value: str) -> bytearray:
    if value == "":
        return bytearray()

    if value.startswith("["):
        items = json.loads(value)
        if not isinstance(items, list):
            msg = f"Expected list in JSON, got {type(items)}"
            raise TypeError(msg)
        return bytearray(items)

    return bytearray(value.encode("utf-8"))
