import types
from dataclasses import fields, is_dataclass
from typing import Annotated, Union, get_args, get_origin, get_type_hints

from dature.fields import PaymentCardNumber, SecretStr
from dature.load_report import FieldOrigin, SourceEntry
from dature.types import JSONValue, TypeAnnotation

try:
    from random_string_detector import RandomStringDetector  # type: ignore[import-untyped]

    _heuristic_detector: RandomStringDetector | None = RandomStringDetector(allow_numbers=True)
except ImportError:
    _heuristic_detector = None

MASK_CHAR = "*"
_MIN_VISIBLE_CHARS = 2
_MIN_LENGTH_FOR_PARTIAL_MASK = 5
_FIXED_MASK_LENGTH = 5
_FULL_MASK = MASK_CHAR * _FIXED_MASK_LENGTH
_MIN_HEURISTIC_LENGTH = 8

DEFAULT_SECRET_PATTERNS: tuple[str, ...] = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "api_secret",
    "access_key",
    "private_key",
    "auth",
    "credential",
)

_secret_paths_cache: dict[tuple[type, tuple[str, ...]], frozenset[str]] = {}


def mask_value(value: str) -> str:
    if len(value) < _MIN_LENGTH_FOR_PARTIAL_MASK:
        return _FULL_MASK
    return value[:_MIN_VISIBLE_CHARS] + _FULL_MASK + value[-_MIN_VISIBLE_CHARS:]


def _is_secret_type(field_type: TypeAnnotation) -> bool:
    queue: list[TypeAnnotation] = [field_type]

    while queue:
        current = queue.pop()

        if current is SecretStr or current is PaymentCardNumber:
            return True

        origin = get_origin(current)
        if origin is Annotated:
            queue.append(get_args(current)[0])
        elif origin is Union or isinstance(current, types.UnionType):
            queue.extend(get_args(current))

    return False


def _matches_secret_pattern(name: str, patterns: tuple[str, ...]) -> bool:
    lower_name = name.lower()
    return any(pattern in lower_name for pattern in patterns)


def _walk_dataclass_fields(
    dataclass_type: type,
    *,
    prefix: str,
    all_patterns: tuple[str, ...],
    result: set[str],
) -> None:
    try:
        hints = get_type_hints(dataclass_type, include_extras=True)
    except Exception:  # noqa: BLE001
        return

    for field in fields(dataclass_type):
        field_name = field.name
        if prefix:
            full_path = f"{prefix}.{field_name}"
        else:
            full_path = field_name

        field_type = hints.get(field_name)
        if field_type is None:
            continue

        if _is_secret_type(field_type) or _matches_secret_pattern(field_name, all_patterns):
            result.add(full_path)

        nested_types = _find_nested_dataclasses(field_type)
        for nested_dc in nested_types:
            _walk_dataclass_fields(
                nested_dc,
                prefix=full_path,
                all_patterns=all_patterns,
                result=result,
            )


def _find_nested_dataclasses(field_type: TypeAnnotation) -> list[type]:
    result: list[type] = []
    queue: list[TypeAnnotation] = [field_type]

    while queue:
        current = queue.pop()

        if is_dataclass(current) and isinstance(current, type):
            result.append(current)
            continue

        origin = get_origin(current)
        if origin is Annotated:
            queue.append(get_args(current)[0])
        elif origin is not None:
            queue.extend(get_args(current))

    return result


def build_secret_paths(
    dataclass_type: type,
    *,
    extra_patterns: tuple[str, ...] = (),
) -> frozenset[str]:
    if not is_dataclass(dataclass_type):
        return frozenset()

    cache_key = (dataclass_type, extra_patterns)
    if cache_key in _secret_paths_cache:
        return _secret_paths_cache[cache_key]

    all_patterns = DEFAULT_SECRET_PATTERNS + extra_patterns
    result: set[str] = set()

    _walk_dataclass_fields(
        dataclass_type,
        prefix="",
        all_patterns=all_patterns,
        result=result,
    )

    frozen = frozenset(result)
    _secret_paths_cache[cache_key] = frozen
    return frozen


def mask_json_value(
    data: JSONValue,
    *,
    secret_paths: frozenset[str],
    _prefix: str = "",
) -> JSONValue:
    if isinstance(data, dict):
        masked: dict[str, JSONValue] = {}
        for key, value in data.items():
            if _prefix:
                child_path = f"{_prefix}.{key}"
            else:
                child_path = key

            if child_path in secret_paths:
                if isinstance(value, str):
                    masked[key] = mask_value(value)
                elif isinstance(value, dict):
                    masked[key] = mask_json_value(value, secret_paths=secret_paths, _prefix=child_path)
                else:
                    masked[key] = mask_value(str(value))
            elif isinstance(value, (dict, list)):
                masked[key] = mask_json_value(value, secret_paths=secret_paths, _prefix=child_path)
            elif isinstance(value, str) and _is_random_string(value):
                masked[key] = mask_value(value)
            else:
                masked[key] = value
        return masked

    if isinstance(data, list):
        return [mask_json_value(item, secret_paths=secret_paths, _prefix=_prefix) for item in data]

    return data


def mask_env_line(line: str) -> str:
    for sep in ("=", ":"):
        if sep in line:
            key, value = line.split(sep, 1)
            return f"{key}{sep}{mask_value(value)}"

    return mask_value(line)


def mask_field_origins(
    origins: tuple[FieldOrigin, ...],
    *,
    secret_paths: frozenset[str],
) -> tuple[FieldOrigin, ...]:
    result: list[FieldOrigin] = []
    for origin in origins:
        if origin.key in secret_paths:
            masked_value: JSONValue = mask_value(str(origin.value))
            result.append(
                FieldOrigin(
                    key=origin.key,
                    value=masked_value,
                    source_index=origin.source_index,
                    source_file=origin.source_file,
                    source_loader_type=origin.source_loader_type,
                ),
            )
        else:
            result.append(origin)
    return tuple(result)


def mask_source_entries(
    entries: tuple[SourceEntry, ...],
    *,
    secret_paths: frozenset[str],
) -> tuple[SourceEntry, ...]:
    result: list[SourceEntry] = []
    for entry in entries:
        masked_raw = mask_json_value(entry.raw_data, secret_paths=secret_paths)
        result.append(
            SourceEntry(
                index=entry.index,
                file_path=entry.file_path,
                loader_type=entry.loader_type,
                raw_data=masked_raw,
            ),
        )
    return tuple(result)


def _is_random_string(value: str) -> bool:
    if len(value) < _MIN_HEURISTIC_LENGTH:
        return False

    if _heuristic_detector is None:
        return False

    try:
        result: bool = _heuristic_detector.is_random_word(value)
    except Exception:  # noqa: BLE001
        return False
    else:
        return result
