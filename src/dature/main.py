from collections.abc import Callable
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, overload

from dature.metadata import LoadMetadata
from dature.sources_loader.env_ import EnvFileLoader, EnvLoader
from dature.sources_loader.ini_ import IniLoader
from dature.sources_loader.json_ import JsonLoader
from dature.sources_loader.toml_ import TomlLoader
from dature.validators.base import DataclassInstance

if TYPE_CHECKING:
    from dature.sources_loader.base import ILoader

LoaderType = Literal["env", "envfile", "yaml", "json", "toml", "ini"]

EXTENSION_MAP: MappingProxyType[str, LoaderType] = MappingProxyType(
    {
        ".env": "envfile",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
    },
)


def _get_loader_class(loader_type: LoaderType) -> type["ILoader"]:
    match loader_type:
        case "env":
            return EnvLoader
        case "envfile":
            return EnvFileLoader
        case "yaml":
            from dature.sources_loader.yaml_ import YamlLoader  # noqa: PLC0415

            return YamlLoader
        case "json":
            return JsonLoader
        case "toml":
            return TomlLoader
        case "ini":
            return IniLoader
        case _:
            msg = f"Unknown loader type: {loader_type}"
            raise ValueError(msg)


def _get_loader_type(metadata: LoadMetadata) -> LoaderType:
    if metadata.loader:
        return metadata.loader

    if not metadata.file_:
        return "env"

    file_path = Path(metadata.file_)

    if (extension := file_path.suffix.lower()) in EXTENSION_MAP:
        return EXTENSION_MAP[extension]

    if file_path.name.startswith(".env"):
        return "envfile"

    supported = ", ".join(EXTENSION_MAP.keys())
    msg = (
        f"Cannot determine loader type for file '{metadata.file_}'. "
        f"Please specify loader explicitly or use a supported extension: {supported}"
    )
    raise ValueError(msg)


def _ensure_retort(loader_instance: "ILoader", cls: type) -> None:
    if cls not in loader_instance._retorts:  # noqa: SLF001
        loader_instance._retorts[cls] = loader_instance._create_retort()  # noqa: SLF001


@overload
def load(
    metadata: LoadMetadata | None,
    /,
    dataclass_: type[DataclassInstance],
) -> DataclassInstance: ...


@overload
def load(
    metadata: LoadMetadata | None = None,
    /,
    dataclass_: None = None,
) -> Callable[[type[DataclassInstance]], type[DataclassInstance]]: ...


def load(  # noqa: C901
    metadata: LoadMetadata | None = None,
    /,
    dataclass_: type[DataclassInstance] | None = None,
) -> DataclassInstance | Callable[[type[DataclassInstance]], type[DataclassInstance]]:
    if metadata is None:
        metadata = LoadMetadata()

    loader_type = _get_loader_type(metadata)
    loader_class = _get_loader_class(loader_type)
    loader_instance = loader_class(
        prefix=metadata.prefix,
        name_style=metadata.name_style,
        field_mapping=metadata.field_mapping,
        root_validators=metadata.root_validators,
    )
    file_path = Path(metadata.file_) if metadata.file_ else Path()

    def _load_config(cls: type[DataclassInstance]) -> type[DataclassInstance]:  # noqa: C901
        if not is_dataclass(cls):
            msg = f"{cls.__name__} must be a dataclass"
            raise TypeError(msg)

        _ensure_retort(loader_instance, cls)
        validating_retort = loader_instance._create_validating_retort(cls)  # noqa: SLF001
        validation_loader = validating_retort.get_loader(cls)
        loaded_data: Any = loader_instance.load(file_path, cls)

        field_list = fields(cls)
        original_init = cls.__init__
        original_post_init = getattr(cls, "__post_init__", None)
        validating = False

        def new_init(self: DataclassInstance, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
            explicit_fields = set(kwargs.keys())
            for i, _ in enumerate(args):
                if i < len(field_list):
                    explicit_fields.add(field_list[i].name)

            complete_kwargs = dict(kwargs)
            for field in field_list:
                if field.name not in explicit_fields:
                    complete_kwargs[field.name] = getattr(loaded_data, field.name)

            original_init(self, *args, **complete_kwargs)

            if original_post_init is None:
                self.__post_init__()

        def new_post_init(self: DataclassInstance) -> None:
            nonlocal validating

            if validating:
                return

            if original_post_init is not None:
                original_post_init(self)

            validating = True
            try:
                obj_dict = asdict(self)
                validation_loader(obj_dict)
            finally:
                validating = False

        cls.__init__ = new_init
        cls.__post_init__ = new_post_init
        return cls

    if dataclass_ is not None:
        _ensure_retort(loader_instance, dataclass_)
        validating_retort = loader_instance._create_validating_retort(dataclass_)  # noqa: SLF001
        validation_loader = validating_retort.get_loader(dataclass_)
        result = loader_instance.load(file_path, dataclass_)
        result_dict = asdict(result)  # type: ignore[call-overload]
        validation_loader(result_dict)
        return result

    return _load_config
