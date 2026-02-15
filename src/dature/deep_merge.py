from dature.error_formatter import ErrorContext, resolve_source_location
from dature.errors import FieldErrorInfo, MergeConflictError, SourceLocation
from dature.metadata import MergeStrategy
from dature.types import JSONValue

_MIN_CONFLICT_SOURCES = 2


def deep_merge_last_wins(base: JSONValue, override: JSONValue) -> JSONValue:
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for key, value in override.items():
            if key in result:
                result[key] = deep_merge_last_wins(result[key], value)
            else:
                result[key] = value
        return result
    return override


def deep_merge_first_wins(base: JSONValue, override: JSONValue) -> JSONValue:
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for key, value in override.items():
            if key in result:
                result[key] = deep_merge_first_wins(result[key], value)
            else:
                result[key] = value
        return result
    return base


def _collect_conflicts(
    dicts: list[JSONValue],
    source_contexts: list[tuple[ErrorContext, str | None]],
    path: list[str],
    conflicts: list[tuple[list[str], list[tuple[int, JSONValue]]]],
) -> None:
    key_sources: dict[str, list[tuple[int, JSONValue]]] = {}

    for i, d in enumerate(dicts):
        if not isinstance(d, dict):
            continue
        for key, value in d.items():
            if key not in key_sources:
                key_sources[key] = []
            key_sources[key].append((i, value))

    for key, sources in key_sources.items():
        if len(sources) < _MIN_CONFLICT_SOURCES:
            continue

        nested_dicts = [v for _, v in sources if isinstance(v, dict)]
        if len(nested_dicts) == len(sources):
            _collect_conflicts(
                [v for _, v in sources],
                [source_contexts[i] for i, _ in sources],
                [*path, key],
                conflicts,
            )
        else:
            conflicts.append(([*path, key], sources))


def raise_on_conflict(
    dicts: list[JSONValue],
    source_ctxs: list[tuple[ErrorContext, str | None]],
    dataclass_name: str,
) -> None:
    conflicts: list[tuple[list[str], list[tuple[int, JSONValue]]]] = []
    _collect_conflicts(dicts, source_ctxs, [], conflicts)

    if not conflicts:
        return

    conflict_errors: list[tuple[FieldErrorInfo, list[SourceLocation]]] = []
    for field_path, sources in conflicts:
        info = FieldErrorInfo(
            field_path=field_path,
            message="Conflicting values in multiple sources",
            input_value=None,
        )
        locations: list[SourceLocation] = []
        for source_idx, _ in sources:
            ctx, file_content = source_ctxs[source_idx]
            loc = resolve_source_location(field_path, ctx, file_content)
            locations.append(loc)
        conflict_errors.append((info, locations))

    raise MergeConflictError(conflict_errors, dataclass_name)


def deep_merge(
    base: JSONValue,
    override: JSONValue,
    *,
    strategy: MergeStrategy,
) -> JSONValue:
    if strategy == MergeStrategy.LAST_WINS:
        return deep_merge_last_wins(base, override)
    if strategy == MergeStrategy.FIRST_WINS:
        return deep_merge_first_wins(base, override)
    msg = "Use merge_sources for RAISE_ON_CONFLICT strategy"
    raise ValueError(msg)
