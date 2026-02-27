from dature.errors import LineRange
from dature.path_finders.base import PathFinder
from dature.path_finders.json_metadata import build_json_line_map


class JsonPathFinder(PathFinder):
    def __init__(self, content: str) -> None:
        self._line_map = build_json_line_map(content)

    def find_line_range(self, target_path: list[str]) -> LineRange | None:
        return self._line_map.get(tuple(target_path))
