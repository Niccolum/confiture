from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class RootValidator:
    func: Callable[..., bool]
    error_message: str = "Root validation failed"

    def get_validator_func(self) -> Callable[..., bool]:
        return self.func

    def get_error_message(self) -> str:
        return self.error_message
