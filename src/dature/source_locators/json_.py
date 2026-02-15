from dataclasses import dataclass


class JsonPathFinder:
    def __init__(self, content: str) -> None:
        self._content = content

    def find_line(self, target_path: list[str]) -> int:
        content = self._content
        length = len(content)
        pos = 0
        line = 1
        stack: list[_StackEntry] = []
        last_key: str | None = None

        while pos < length:
            ch = content[pos]

            if ch in " \t\r\n":
                if ch == "\n":
                    line += 1
                pos += 1
                continue

            if ch == ",":
                pos += 1
                continue

            if ch in "{[":
                _increment_parent_array(stack)
                is_array = ch == "["
                stack.append(_StackEntry(key=last_key, is_array=is_array, array_index=-1))
                pos += 1
                last_key = None
                continue

            if ch in "}]":
                if stack:
                    stack.pop()
                pos += 1
                last_key = None
                continue

            if ch != '"':
                _increment_parent_array(stack)
                pos = _skip_scalar(content, pos, length)
                continue

            result = _handle_string(content, pos, length, stack, target_path)
            pos = result.pos
            last_key = result.last_key
            if result.found:
                return line

        return -1


@dataclass
class _StackEntry:
    key: str | None
    is_array: bool
    array_index: int


@dataclass(frozen=True, slots=True)
class _StringResult:
    pos: int
    last_key: str | None
    found: bool


def _handle_string(
    content: str,
    pos: int,
    length: int,
    stack: list[_StackEntry],
    target_path: list[str],
) -> _StringResult:
    string_start = pos + 1
    end_pos = _skip_string(content, string_start)
    string_value = content[string_start : end_pos - 1]

    colon_pos = _skip_ws(content, end_pos, length)

    if colon_pos >= length or content[colon_pos] != ":":
        _increment_parent_array(stack)
        return _StringResult(pos=end_pos, last_key=None, found=False)

    if _build_path(stack, string_value) == target_path:
        return _StringResult(pos=end_pos, last_key=None, found=True)

    return _StringResult(pos=colon_pos + 1, last_key=string_value, found=False)


def _increment_parent_array(stack: list[_StackEntry]) -> None:
    if stack and stack[-1].is_array:
        stack[-1].array_index += 1


def _skip_string(content: str, pos: int) -> int:
    """Advance past a JSON string body. Returns position after the closing quote."""
    length = len(content)
    while pos < length:
        ch = content[pos]
        if ch == "\\":
            pos += 2
            continue
        if ch == '"':
            return pos + 1
        pos += 1
    return pos


def _skip_ws(content: str, pos: int, length: int) -> int:
    while pos < length and content[pos] in " \t\r\n":
        pos += 1
    return pos


def _skip_scalar(content: str, pos: int, length: int) -> int:
    while pos < length and content[pos] not in " \t\r\n,}]":
        pos += 1
    return pos


def _build_path(stack: list[_StackEntry], current_key: str) -> list[str]:
    path: list[str] = []
    for entry in stack:
        if entry.key is not None:
            path.append(entry.key)
        if entry.is_array:
            path.append(str(entry.array_index))
    path.append(current_key)
    return path
