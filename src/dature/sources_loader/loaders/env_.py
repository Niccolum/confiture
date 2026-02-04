import json
import re
from typing import Any, cast

from dature.sources_loader.loaders.common import bool_from_string
from dature.types import JSONValue


def dict_from_env_nested(value: str | dict[Any, Any]) -> dict[Any, Any]:
    if isinstance(value, str):
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

    if isinstance(value, dict):
        result: dict[Any, Any] = {}
        for k, v in value.items():
            if isinstance(v, dict):
                result[k] = dict_from_env_nested(v)
            elif isinstance(v, str):
                result[k] = _infer_type(v)
            else:
                result[k] = v

        if all(k.isdigit() for k in result if isinstance(k, str)):
            return {int(k): v for k, v in result.items()}

        return result

    return value


def _infer_type(value: str) -> JSONValue:
    if value == "":
        return value

    try:
        return bool_from_string(value)
    except TypeError:
        pass

    if value.startswith(("[", "{")):
        try:
            return cast("JSONValue", json.loads(value))
        except json.JSONDecodeError:
            pass

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    return value
