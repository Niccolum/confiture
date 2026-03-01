from toml_rs._lib import TomlVersion

from dature.errors.exceptions import LineRange
from dature.path_finders.base import PathFinder
from dature.path_finders.toml_metadata import build_toml_line_map


class TomlPathFinder(PathFinder):
    def __init__(self, content: str, *, toml_version: TomlVersion) -> None:
        self._line_map = build_toml_line_map(content, toml_version)

    def find_line_range(self, target_path: list[str]) -> LineRange | None:
        return self._line_map.get(tuple(target_path))


class Toml10PathFinder(TomlPathFinder):
    def __init__(self, content: str) -> None:
        super().__init__(content, toml_version="1.0.0")


class Toml11PathFinder(TomlPathFinder):
    def __init__(self, content: str) -> None:
        super().__init__(content, toml_version="1.1.0")
