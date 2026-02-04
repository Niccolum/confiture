def bytes_from_string(value: str) -> bytes:
    return value.encode("utf-8")


def complex_from_string(value: str) -> complex:
    return complex(value.replace(" ", ""))
