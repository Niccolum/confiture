from collections.abc import Callable
from typing import Any, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: dict[str, Any]


class ValidatorProtocol(Protocol):
    def get_validator_func(self) -> Callable[..., bool]: ...

    def get_error_message(self) -> str: ...
