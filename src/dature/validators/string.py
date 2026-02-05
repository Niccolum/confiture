import re
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class MinLength:
    value: int
    error_message: str = "Value must have at least {value} characters"

    def get_validator_func(self) -> Callable[[str], bool]:
        def validate(val: str) -> bool:
            return len(val) >= self.value

        return validate

    def get_error_message(self) -> str:
        return self.error_message.format(value=self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class MaxLength:
    value: int
    error_message: str = "Value must have at most {value} characters"

    def get_validator_func(self) -> Callable[[str], bool]:
        def validate(val: str) -> bool:
            return len(val) <= self.value

        return validate

    def get_error_message(self) -> str:
        return self.error_message.format(value=self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class RegexPattern:
    pattern: str
    error_message: str = "Value must match pattern '{pattern}'"

    def get_validator_func(self) -> Callable[[str], bool]:
        def validate(val: str) -> bool:
            return bool(re.match(self.pattern, val))

        return validate

    def get_error_message(self) -> str:
        return self.error_message.format(pattern=self.pattern)
