import abc
from pathlib import Path
from typing import TypeVar

from adaptix import Retort, loader
from adaptix.provider import Provider

from dature.sources_loader.loaders.base import bytes_from_string, complex_from_string
from dature.types import DotSeparatedPath, JSONValue

T = TypeVar("T")


class ILoader(abc.ABC):
    def __init__(self, prefix: DotSeparatedPath | None = None) -> None:
        self._prefix = prefix
        self._retort = self._create_retort()

    def _get_additional_loaders(self) -> list[Provider]:
        return []

    def _create_retort(self) -> Retort:
        default_loaders: list[Provider] = [
            loader(bytes, bytes_from_string),
            loader(complex, complex_from_string),
        ]
        return Retort(strict_coercion=False, recipe=default_loaders + self._get_additional_loaders())

    @abc.abstractmethod
    def _load(self, path: Path) -> JSONValue: ...

    def _apply_prefix(self, data: JSONValue) -> JSONValue:
        if not self._prefix:
            return data

        for key in self._prefix.split("."):
            if not isinstance(data, dict):
                return {}
            if key not in data:
                return {}
            data = data[key]

        return data

    def _pre_processing(self, data: JSONValue) -> JSONValue:
        return self._apply_prefix(data)

    def _transform_to_dataclass(self, data: JSONValue, dataclass_: type[T]) -> T:
        return self._retort.load(data, dataclass_)

    def load(self, path: Path, dataclass_: type[T]) -> T:
        data = self._load(path)
        pre_processed_data = self._pre_processing(data)
        return self._transform_to_dataclass(pre_processed_data, dataclass_)
        return self._transform_to_dataclass(pre_processed_data, dataclass_)
