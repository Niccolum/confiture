from ruamel.yaml.docinfo import Version

from dature.errors import LineRange
from dature.path_finders.base import PathFinder
from dature.path_finders.yaml_metadata import build_yaml_line_map


class YamlPathFinder(PathFinder):
    def __init__(self, content: str, *, yaml_version: Version) -> None:
        self._line_map = build_yaml_line_map(content, yaml_version)

    def find_line_range(self, target_path: list[str]) -> LineRange | None:
        return self._line_map.get(tuple(target_path))


class Yaml11PathFinder(YamlPathFinder):
    def __init__(self, content: str) -> None:
        super().__init__(content, yaml_version=Version(1, 1))


class Yaml12PathFinder(YamlPathFinder):
    def __init__(self, content: str) -> None:
        super().__init__(content, yaml_version=Version(1, 2))
