from dature.errors import LineRange
from dature.path_finders.base import PathFinder
from dature.path_finders.ini_metadata import MetadataConfigParser

_MIN_INI_PATH_DEPTH = 2


class TablePathFinder(PathFinder):
    def __init__(self, content: str) -> None:
        parser = MetadataConfigParser()
        parser.read_string(content)
        self._line_map = parser.line_metadata

    def find_line_range(self, target_path: list[str]) -> LineRange | None:
        if len(target_path) < _MIN_INI_PATH_DEPTH:
            return None
        section = ".".join(target_path[:-1])
        option = target_path[-1]
        return self._line_map.get((section, option))
