import abc
from datetime import date, datetime, time
from pathlib import Path
from typing import cast

from adaptix import loader
from adaptix.provider import Provider
from ruamel.yaml import YAML

from dature.sources_loader.base import ILoader
from dature.sources_loader.loaders import (
    bytearray_from_string,
    date_passthrough,
    datetime_passthrough,
    time_from_int,
    time_from_string,
)
from dature.types import JSONValue


class BaseYamlLoader(ILoader, abc.ABC):
    @abc.abstractmethod
    def _yaml_version(self) -> tuple[int, int]: ...

    def _load(self, path: Path) -> JSONValue:
        yaml = YAML(typ="safe")
        yaml.version = self._yaml_version()
        with path.open() as file_:
            return cast("JSONValue", yaml.load(file_))


class Yaml11Loader(BaseYamlLoader):
    def _yaml_version(self) -> tuple[int, int]:
        return (1, 1)

    def _additional_loaders(self) -> list[Provider]:
        return [
            loader(date, date_passthrough),
            loader(datetime, datetime_passthrough),
            loader(time, time_from_int),
            loader(bytearray, bytearray_from_string),
        ]


class Yaml12Loader(BaseYamlLoader):
    def _yaml_version(self) -> tuple[int, int]:
        return (1, 2)

    def _additional_loaders(self) -> list[Provider]:
        return [
            loader(date, date_passthrough),
            loader(datetime, datetime_passthrough),
            loader(time, time_from_string),
            loader(bytearray, bytearray_from_string),
        ]
