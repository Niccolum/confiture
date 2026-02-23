import toml_rs
from toml_rs._lib import TomlVersion

from dature.errors import LineRange


def build_toml_line_map(content: str, toml_version: TomlVersion) -> dict[tuple[str, ...], LineRange]:
    doc = toml_rs.load_with_metadata(content, toml_version=toml_version)
    line_map: dict[tuple[str, ...], LineRange] = {}
    for key_meta in doc.meta["keys"].values():
        path = _parse_meta_key(key_meta["key"])

        key_line = key_meta["key_line"]
        value_line = key_meta["value_line"]
        if isinstance(value_line, tuple):
            end = value_line[1]
        else:
            end = value_line

        if key_line < 1:
            # fallback for inline tables (key_line=0 bug in toml_rs)
            if isinstance(value_line, tuple):
                key_line = value_line[0]
            else:
                key_line = value_line

        line_map[path] = LineRange(start=key_line, end=end)
    return line_map


def _parse_meta_key(meta_key: str) -> tuple[str, ...]:
    """Parses dot-separated key from metadata respecting quotes.

    Examples:
      'database.host'        -> ('database', 'host')
      'a."b.c"'              -> ('a', 'b.c')
      'section."dotted.key"' -> ('section', 'dotted.key')
    """
    parts: list[str] = []
    i = 0
    while i < len(meta_key):
        if meta_key[i] == '"':
            end = meta_key.index('"', i + 1)
            parts.append(meta_key[i + 1 : end])
            i = end + 1
            if i < len(meta_key) and meta_key[i] == ".":
                i += 1
        else:
            dot = meta_key.find(".", i)
            if dot == -1:
                parts.append(meta_key[i:])
                break
            parts.append(meta_key[i:dot])
            i = dot + 1
    return tuple(parts)
