from collections.abc import Callable
from typing import Annotated, Any, Protocol, get_args, get_origin

from adaptix import P, validator
from adaptix.provider import Provider


class DataclassInstance(Protocol):
    __dataclass_fields__: dict[str, Any]


class ValidatorProtocol(Protocol):
    def get_validator_func(self) -> Callable[..., bool]: ...

    def get_error_message(self) -> str: ...


class RootValidatorProtocol(Protocol):
    def __call__(self, obj: DataclassInstance) -> bool: ...


def extract_validators_from_type(field_type: object) -> list[ValidatorProtocol]:
    validators: list[ValidatorProtocol] = []

    if get_origin(field_type) is not Annotated:
        return validators

    args = get_args(field_type)

    validators.extend(arg for arg in args[1:] if hasattr(arg, "__dataclass_fields__"))

    return validators


def create_validator_providers(
    dataclass_: type,
    field_name: str,
    validators: list[ValidatorProtocol],
) -> list[Provider]:
    providers = []

    for v in validators:
        func = v.get_validator_func()
        error = v.get_error_message()
        provider = validator(
            P[dataclass_][field_name],
            func,
            error,
        )
        providers.append(provider)

    return providers


def create_root_validator_providers(
    dataclass_: type,
    root_validators: tuple[RootValidatorProtocol, ...],
) -> list[Provider]:
    providers = []

    for root_validator_func in root_validators:
        provider = validator(
            P[dataclass_],
            root_validator_func,
            "Root validation failed",
        )
        providers.append(provider)

    return providers
