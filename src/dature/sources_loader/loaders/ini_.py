import json
import re
from typing import Any


def dict_from_json_string(value: str | dict[Any, Any]) -> dict[Any, Any]:
    if isinstance(value, dict):
        return value

    if value == "":
        return {}

    value_fixed = re.sub(r"(\{|,)\s*(\d+)\s*:", r'\1"\2":', value)
    parsed = json.loads(value_fixed)

    if not isinstance(parsed, dict):
        msg = f"Expected dict in JSON, got {type(parsed)}"
        raise TypeError(msg)

    if all(k.isdigit() for k in parsed if isinstance(k, str)):
        return {int(k): v for k, v in parsed.items()}

    return parsed
