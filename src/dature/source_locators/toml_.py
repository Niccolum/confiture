class TomlPathFinder:
    def __init__(self, content: str) -> None:
        self.lines = content.splitlines()

    def find_line(self, target_path: list[str]) -> int:
        target_key = target_path[-1]
        target_parents = target_path[:-1]
        current_section: list[str] = []
        in_multiline: str | None = None

        for i, line in enumerate(self.lines, 1):
            if in_multiline is not None:
                if in_multiline in line:
                    in_multiline = None
                continue

            stripped = line.strip()
            if not stripped or stripped.startswith(("#", ";")):
                continue

            # Working with sections [section] or [parent.child]
            if stripped.startswith("[") and "]" in stripped:
                section_name = stripped.strip("[] ")
                current_section = [p.strip() for p in section_name.split(".")]
                continue

            # Working with keys key = value
            if "=" not in stripped:
                continue

            key, _, value = stripped.partition("=")
            key = key.strip().strip("\"'")
            value = value.strip()

            in_multiline = _detect_unclosed_multiline(value)
            if in_multiline is not None:
                continue

            if key == target_key and current_section == target_parents:
                return i
        return -1


def _detect_unclosed_multiline(value: str) -> str | None:
    for delimiter in ('"""', "'''"):
        if delimiter not in value:
            continue
        # odd number of delimiters means unclosed
        count = value.count(delimiter)
        if count % 2 == 1:
            return delimiter
    return None
