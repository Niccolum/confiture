from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.docinfo import Version
from ruamel.yaml.scalarstring import ScalarString

from dature.errors.exceptions import LineRange


def build_yaml_line_map(content: str, yaml_version: Version) -> dict[tuple[str, ...], LineRange]:
    yaml = YAML(typ="rt")
    yaml.version = yaml_version
    data = yaml.load(StringIO(content))
    if not isinstance(data, CommentedMap):
        return {}

    lines = content.splitlines()
    total_lines = len(lines)
    line_map: dict[tuple[str, ...], LineRange] = {}
    _walk_mapping(data, (), line_map, lines, total_lines)
    return line_map


def _last_non_empty_line_before(lines: list[str], before_0based: int, after_0based: int) -> int:
    """Returns 1-based line number of last non-empty line in [after_0based, before_0based)."""
    for i in range(before_0based - 1, after_0based - 1, -1):
        if lines[i].strip():
            return i + 1
    return after_0based + 1


def _walk_mapping(
    mapping: CommentedMap,
    parent_path: tuple[str, ...],
    line_map: dict[tuple[str, ...], LineRange],
    lines: list[str],
    parent_end_1based: int,
) -> None:
    keys = list(mapping.keys())
    lc_data = mapping.lc.data

    for idx, key in enumerate(keys):
        key_str = str(key)
        current_path = (*parent_path, key_str)

        key_line_0, _key_col, val_line_0, _val_col = lc_data[key]
        start_1based = key_line_0 + 1

        value = mapping[key]

        if isinstance(value, CommentedMap):
            if idx + 1 < len(keys):
                next_key = keys[idx + 1]
                next_key_line_0 = lc_data[next_key][0]
                end_1based = _last_non_empty_line_before(lines, next_key_line_0, key_line_0)
            else:
                end_1based = _last_non_empty_line_before(lines, parent_end_1based, key_line_0)

            line_map[current_path] = LineRange(start=start_1based, end=end_1based)
            _walk_mapping(value, current_path, line_map, lines, end_1based)

        elif isinstance(value, CommentedSeq):
            if idx + 1 < len(keys):
                next_key = keys[idx + 1]
                next_key_line_0 = lc_data[next_key][0]
                end_1based = _last_non_empty_line_before(lines, next_key_line_0, key_line_0)
            else:
                end_1based = _last_non_empty_line_before(lines, parent_end_1based, key_line_0)

            line_map[current_path] = LineRange(start=start_1based, end=end_1based)

        else:
            is_block_scalar = isinstance(value, ScalarString) and "\n" in str(value)

            if key_line_0 == val_line_0 and not is_block_scalar:
                line_map[current_path] = LineRange(start=start_1based, end=start_1based)
            else:
                if idx + 1 < len(keys):
                    next_key = keys[idx + 1]
                    next_key_line_0 = lc_data[next_key][0]
                    end_1based = _last_non_empty_line_before(lines, next_key_line_0, key_line_0)
                else:
                    end_1based = _last_non_empty_line_before(lines, parent_end_1based, key_line_0)

                line_map[current_path] = LineRange(start=start_1based, end=end_1based)
