from dataclasses import dataclass


@dataclass
class _StackEntry:
    key: str | None
    is_array: bool
    array_index: int


@dataclass
class _ParseState:
    pos: int
    line: int
    last_key: str | None


@dataclass(frozen=True, slots=True)
class _PosLine:
    pos: int
    line: int


@dataclass(frozen=True, slots=True)
class _KeyResult:
    pos: int
    line: int
    last_key: str | None
    found: bool


class Json5PathFinder:
    def __init__(self, content: str) -> None:
        self._content = content

    def find_line(self, target_path: list[str]) -> int:
        content = self._content
        length = len(content)
        state = _ParseState(pos=0, line=1, last_key=None)
        stack: list[_StackEntry] = []

        while state.pos < length:
            ch = content[state.pos]

            if _try_skip_noise(ch, content, state, length):
                continue

            if ch in "{[":
                _increment_parent_array(stack)
                is_array = ch == "["
                stack.append(_StackEntry(key=state.last_key, is_array=is_array, array_index=-1))
                state.pos += 1
                state.last_key = None
                continue

            if ch in "}]":
                if stack:
                    stack.pop()
                state.pos += 1
                state.last_key = None
                continue

            if ch in {'"', "'"}:
                result = _handle_quoted(content, state, length, stack, target_path)
                if result.found:
                    return result.line
                state.pos = result.pos
                state.line = result.line
                state.last_key = result.last_key
                continue

            if _is_ident_start(ch):
                result = _handle_identifier(content, state, length, stack, target_path)
                if result.found:
                    return result.line
                state.pos = result.pos
                state.line = result.line
                state.last_key = result.last_key
                continue

            _increment_parent_array(stack)
            state.pos = _skip_scalar(content, state.pos, length)

        return -1


def _try_skip_noise(ch: str, content: str, state: _ParseState, length: int) -> bool:
    if ch in " \t\r\n":
        if ch == "\n":
            state.line += 1
        state.pos += 1
        return True

    if ch == ",":
        state.pos += 1
        return True

    if ch != "/" or state.pos + 1 >= length:
        return False

    next_ch = content[state.pos + 1]
    if next_ch == "/":
        state.pos = _skip_line_comment(content, state.pos + 2, length)
        return True
    if next_ch == "*":
        block = _skip_block_comment(content, state.pos + 2, length, state.line)
        state.pos = block.pos
        state.line = block.line
        return True

    return False


def _handle_quoted(
    content: str,
    state: _ParseState,
    length: int,
    stack: list[_StackEntry],
    target_path: list[str],
) -> _KeyResult:
    quote = content[state.pos]
    string_start = state.pos + 1
    end = _skip_quoted_string(content, string_start, quote, state.line)
    string_value = content[string_start : end.pos - 1]

    colon = _skip_ws_and_comments(content, end.pos, length, end.line)

    if colon.pos >= length or content[colon.pos] != ":":
        _increment_parent_array(stack)
        return _KeyResult(pos=end.pos, line=end.line, last_key=None, found=False)

    if _build_path(stack, string_value) == target_path:
        return _KeyResult(pos=end.pos, line=state.line, last_key=None, found=True)

    return _KeyResult(pos=colon.pos + 1, line=colon.line, last_key=string_value, found=False)


def _handle_identifier(
    content: str,
    state: _ParseState,
    length: int,
    stack: list[_StackEntry],
    target_path: list[str],
) -> _KeyResult:
    ident_end = _skip_identifier(content, state.pos, length)
    ident = content[state.pos : ident_end]

    colon = _skip_ws_and_comments(content, ident_end, length, state.line)

    if colon.pos >= length or content[colon.pos] != ":":
        _increment_parent_array(stack)
        return _KeyResult(pos=ident_end, line=state.line, last_key=None, found=False)

    if _build_path(stack, ident) == target_path:
        return _KeyResult(pos=ident_end, line=state.line, last_key=None, found=True)

    return _KeyResult(pos=colon.pos + 1, line=colon.line, last_key=ident, found=False)


def _increment_parent_array(stack: list[_StackEntry]) -> None:
    if stack and stack[-1].is_array:
        stack[-1].array_index += 1


def _build_path(stack: list[_StackEntry], current_key: str) -> list[str]:
    path: list[str] = []
    for entry in stack:
        if entry.key is not None:
            path.append(entry.key)
        if entry.is_array:
            path.append(str(entry.array_index))
    path.append(current_key)
    return path


def _skip_quoted_string(
    content: str,
    pos: int,
    quote: str,
    line: int,
) -> _PosLine:
    """Advance past a quoted string body. Returns position after the closing quote."""
    length = len(content)
    while pos < length:
        ch = content[pos]
        if ch == "\\":
            if pos + 1 < length and content[pos + 1] == "\n":
                line += 1
            pos += 2
            continue
        if ch == "\n":
            line += 1
            pos += 1
            continue
        if ch == quote:
            return _PosLine(pos=pos + 1, line=line)
        pos += 1
    return _PosLine(pos=pos, line=line)


def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch in {"_", "$"}


def _is_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch in {"_", "$"}


def _skip_identifier(content: str, pos: int, length: int) -> int:
    while pos < length and _is_ident_char(content[pos]):
        pos += 1
    return pos


def _skip_line_comment(content: str, pos: int, length: int) -> int:
    while pos < length and content[pos] != "\n":
        pos += 1
    return pos


def _skip_block_comment(
    content: str,
    pos: int,
    length: int,
    line: int,
) -> _PosLine:
    while pos < length:
        if content[pos] == "\n":
            line += 1
        elif content[pos] == "*" and pos + 1 < length and content[pos + 1] == "/":
            return _PosLine(pos=pos + 2, line=line)
        pos += 1
    return _PosLine(pos=pos, line=line)


def _skip_ws_and_comments(
    content: str,
    pos: int,
    length: int,
    line: int,
) -> _PosLine:
    while pos < length:
        ch = content[pos]
        if ch in " \t\r":
            pos += 1
            continue
        if ch == "\n":
            line += 1
            pos += 1
            continue
        if ch == "/" and pos + 1 < length and content[pos + 1] == "/":
            pos = _skip_line_comment(content, pos + 2, length)
            continue
        if ch == "/" and pos + 1 < length and content[pos + 1] == "*":
            block = _skip_block_comment(content, pos + 2, length, line)
            pos = block.pos
            line = block.line
            continue
        return _PosLine(pos=pos, line=line)
    return _PosLine(pos=pos, line=line)


def _skip_scalar(content: str, pos: int, length: int) -> int:
    while pos < length and content[pos] not in " \t\r\n,}]":
        pos += 1
    return pos
