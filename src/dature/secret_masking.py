import types
from dataclasses import fields, is_dataclass
from typing import Annotated, Union, get_args, get_origin, get_type_hints

from dature.config import config
from dature.fields.payment_card import PaymentCardNumber
from dature.fields.secret_str import SecretStr
from dature.load_report import FieldOrigin, SourceEntry
from dature.types import JSONValue, TypeAnnotation

try:
    from random_string_detector import RandomStringDetector  # type: ignore[import-untyped]

    _heuristic_detector: RandomStringDetector | None = RandomStringDetector(allow_numbers=True)
except ImportError:
    _heuristic_detector = None

_secret_paths_cache: dict[tuple[type, tuple[str, ...]], frozenset[str]] = {}


def mask_value(value: str) -> str:
    cfg = config.masking
    full_mask = cfg.mask_char * cfg.fixed_mask_length
    if len(value) < cfg.min_length_for_partial_mask:
        return full_mask
    return value[: cfg.min_visible_chars] + full_mask + value[-cfg.min_visible_chars :]


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

    all_patterns = config.masking.secret_field_names + extra_patterns
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
            key, raw_value = line.split(sep, 1)
            return f"{key}{sep}{_mask_raw_value(raw_value)}"

    return mask_value(line)


def _mask_raw_value(raw: str) -> str:
    stripped = raw.lstrip(" ")
    leading_spaces = raw[: len(raw) - len(stripped)]

    for quote in ('"', "'"):
        if stripped.startswith(quote):
            inner_start = 1
            end_idx = stripped.find(quote, inner_start)
            if end_idx == -1:
                break
            inner = stripped[inner_start:end_idx]
            suffix = stripped[end_idx + 1 :]
            return f"{leading_spaces}{quote}{mask_value(inner)}{quote}{suffix}"

    return f"{leading_spaces}{mask_value(stripped)}"


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
    if len(value) < config.masking.min_heuristic_length:
        return False

    if _heuristic_detector is None:
        return False

    try:
        result: bool = _heuristic_detector.is_random_word(value)
    except Exception:  # noqa: BLE001
        return False
    else:
        return result
