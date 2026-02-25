from typing import TYPE_CHECKING, cast

import toml_rs
from toml_rs._lib import TomlVersion

from dature.errors import LineRange

if TYPE_CHECKING:
    from toml_rs._toml_rs import KeyMeta


def build_toml_line_map(content: str, toml_version: TomlVersion) -> dict[tuple[str, ...], LineRange]:
    doc = toml_rs.load_with_metadata(content, toml_version=toml_version)
    line_map: dict[tuple[str, ...], LineRange] = {}
    _walk_nodes(doc.meta["nodes"], (), line_map)
    return line_map


def _walk_nodes(
    nodes: "dict[str, KeyMeta]",
    prefix: tuple[str, ...],
    line_map: dict[tuple[str, ...], LineRange],
) -> None:
    for name, node in nodes.items():
        if not isinstance(node, dict):
            continue
        path = (*prefix, name)
        if "key" not in node:
            # section header (e.g. [database]) — recurse into children
            _walk_nodes(cast("dict[str, KeyMeta]", node), path, line_map)
            continue
        _process_leaf_or_inline_table(node, path, line_map)


def _process_leaf_or_inline_table(
    node: "KeyMeta",
    path: tuple[str, ...],
    line_map: dict[tuple[str, ...], LineRange],
) -> None:
    start = node["key_line"]
    value_line = node["value_line"]

    if isinstance(value_line, tuple):
        end = value_line[1]
    else:
        end = value_line

    line_map[path] = LineRange(start=start, end=end)

    value = node.get("value")
    if isinstance(value, dict):
        # inline table — recurse into children
        _walk_nodes(cast("dict[str, KeyMeta]", value), path, line_map)
