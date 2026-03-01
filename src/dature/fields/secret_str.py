class SecretStr:
    __slots__ = ("_secret_value",)

    def __init__(self, secret_value: str) -> None:
        self._secret_value = secret_value

    def get_secret_value(self) -> str:
        return self._secret_value

    def __str__(self) -> str:
        return "**********"

    def __repr__(self) -> str:
        return "SecretStr('**********')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretStr):
            return NotImplemented
        return self._secret_value == other._secret_value

    def __hash__(self) -> int:
        return hash(self._secret_value)

    def __len__(self) -> int:
        return len(self._secret_value)
