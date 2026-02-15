import logging
from collections.abc import Callable
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Any

from dature.error_formatter import ErrorContext, handle_load_errors
from dature.errors import DatureConfigError
from dature.load_report import (
    FieldOrigin,
    LoadReport,
    SourceEntry,
    attach_load_report,
)
from dature.metadata import LoadMetadata
from dature.sources_loader.base import ILoader
from dature.sources_loader.resolver import get_loader_type
from dature.types import JSONValue
from dature.validators.protocols import DataclassInstance

logger = logging.getLogger("dature")


def merge_fields(
    loaded_data: Any,  # noqa: ANN401
    field_list: tuple[Any, ...],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    explicit_fields = set(kwargs.keys())
    for i, _ in enumerate(args):
        if i < len(field_list):
            explicit_fields.add(field_list[i].name)

    complete_kwargs = dict(kwargs)
    for field in field_list:
        if field.name not in explicit_fields:
            complete_kwargs[field.name] = getattr(loaded_data, field.name)

    return complete_kwargs


def ensure_retort(loader_instance: ILoader, cls: type) -> None:
    """Creates a replacement response to __init__ so that Adaptix sees the original signature."""
    if cls not in loader_instance.retorts:
        loader_instance.retorts[cls] = loader_instance.create_retort()
    loader_instance.retorts[cls].get_loader(cls)


def _log_single_source_load(
    *,
    dataclass_name: str,
    loader_type: str,
    file_path: str,
    data: JSONValue,
) -> None:
    logger.debug(
        "[%s] Single-source load: loader=%s, file=%s",
        dataclass_name,
        loader_type,
        file_path,
    )
    logger.debug(
        "[%s] Loaded data: %s",
        dataclass_name,
        data,
    )


def _build_single_source_report(
    *,
    dataclass_name: str,
    loader_type: str,
    file_path: str | None,
    raw_data: JSONValue,
) -> LoadReport:
    source = SourceEntry(
        index=0,
        file_path=file_path,
        loader_type=loader_type,
        raw_data=raw_data,
    )

    origins: list[FieldOrigin] = []
    if isinstance(raw_data, dict):
        for key, value in sorted(raw_data.items()):
            origins.append(
                FieldOrigin(
                    key=key,
                    value=value,
                    source_index=0,
                    source_file=file_path,
                    source_loader_type=loader_type,
                ),
            )

    return LoadReport(
        dataclass_name=dataclass_name,
        strategy=None,
        sources=(source,),
        field_origins=tuple(origins),
        merged_data=raw_data,
    )


class _PatchContext:
    def __init__(
        self,
        *,
        loader_instance: ILoader,
        file_path: Path,
        cls: type[DataclassInstance],
        metadata: LoadMetadata,
        cache: bool,
        debug: bool,
    ) -> None:
        ensure_retort(loader_instance, cls)
        validating_retort = loader_instance.create_validating_retort(cls)

        self.loader_instance = loader_instance
        self.file_path = file_path
        self.cls = cls
        self.metadata = metadata
        self.cache = cache
        self.debug = debug
        self.cached_data: DataclassInstance | None = None
        self.field_list = fields(cls)
        self.original_init = cls.__init__
        self.original_post_init = getattr(cls, "__post_init__", None)
        self.validation_loader = validating_retort.get_loader(cls)
        self.validating = False
        self.loading = False

        self.loader_type = get_loader_type(metadata)
        self.error_file_path = Path(metadata.file_) if metadata.file_ else None
        self.prefix = metadata.prefix
        self.split_symbols = metadata.split_symbols
        self.error_ctx = ErrorContext(
            dataclass_name=cls.__name__,
            loader_type=self.loader_type,
            file_path=self.error_file_path,
            prefix=self.prefix,
            split_symbols=self.split_symbols,
        )


def _make_new_init(ctx: _PatchContext) -> Callable[..., None]:
    def new_init(self: DataclassInstance, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        if ctx.loading:
            ctx.original_init(self, *args, **kwargs)
            return

        if ctx.cache and ctx.cached_data is not None:
            loaded_data = ctx.cached_data
        else:
            ctx.loading = True
            try:
                loaded_data = handle_load_errors(
                    func=lambda: ctx.loader_instance.load(ctx.file_path, ctx.cls),
                    ctx=ctx.error_ctx,
                )
            finally:
                ctx.loading = False

            _log_single_source_load(
                dataclass_name=ctx.cls.__name__,
                loader_type=ctx.loader_type,
                file_path=str(ctx.file_path),
                data=asdict(loaded_data),
            )

            if ctx.cache:
                ctx.cached_data = loaded_data

        complete_kwargs = merge_fields(loaded_data, ctx.field_list, args, kwargs)
        ctx.original_init(self, *args, **complete_kwargs)

        if ctx.debug:
            result_dict = asdict(self)
            report = _build_single_source_report(
                dataclass_name=ctx.cls.__name__,
                loader_type=ctx.loader_type,
                file_path=str(ctx.file_path) if ctx.metadata.file_ is not None else None,
                raw_data=result_dict,
            )
            attach_load_report(self, report)

        if ctx.original_post_init is None:
            self.__post_init__()  # type: ignore[attr-defined]

    return new_init


def _make_new_post_init(ctx: _PatchContext) -> Callable[..., None]:
    def new_post_init(self: DataclassInstance) -> None:
        if ctx.loading:
            return

        if ctx.validating:
            return

        if ctx.original_post_init is not None:
            ctx.original_post_init(self)

        ctx.validating = True
        try:
            obj_dict = asdict(self)
            handle_load_errors(
                func=lambda: ctx.validation_loader(obj_dict),
                ctx=ctx.error_ctx,
            )
        finally:
            ctx.validating = False

    return new_post_init


def load_as_function(
    *,
    loader_instance: ILoader,
    file_path: Path,
    dataclass_: type[DataclassInstance],
    metadata: LoadMetadata,
    debug: bool,
) -> DataclassInstance:
    loader_type = get_loader_type(metadata)
    error_file_path = Path(metadata.file_) if metadata.file_ else None
    error_ctx = ErrorContext(
        dataclass_name=dataclass_.__name__,
        loader_type=loader_type,
        file_path=error_file_path,
        prefix=metadata.prefix,
        split_symbols=metadata.split_symbols,
    )

    raw_data = handle_load_errors(
        func=lambda: loader_instance.load_raw(file_path),
        ctx=error_ctx,
    )

    report: LoadReport | None = None
    if debug:
        report = _build_single_source_report(
            dataclass_name=dataclass_.__name__,
            loader_type=loader_type,
            file_path=metadata.file_,
            raw_data=raw_data,
        )

    _log_single_source_load(
        dataclass_name=dataclass_.__name__,
        loader_type=loader_type,
        file_path=str(file_path),
        data=raw_data if isinstance(raw_data, dict) else {},
    )

    try:
        result = handle_load_errors(
            func=lambda: loader_instance.transform_to_dataclass(raw_data, dataclass_),
            ctx=error_ctx,
        )
    except DatureConfigError:
        if report is not None:
            attach_load_report(dataclass_, report)
        raise

    result_dict = asdict(result)

    validating_retort = loader_instance.create_validating_retort(dataclass_)
    validation_loader = validating_retort.get_loader(dataclass_)

    try:
        handle_load_errors(
            func=lambda: validation_loader(result_dict),
            ctx=error_ctx,
        )
    except DatureConfigError:
        if report is not None:
            attach_load_report(dataclass_, report)
        raise

    if report is not None:
        attach_load_report(result, report)

    return result


def make_decorator(
    *,
    loader_instance: ILoader,
    file_path: Path,
    metadata: LoadMetadata,
    cache: bool = True,
    debug: bool = False,
) -> Callable[[type[DataclassInstance]], type[DataclassInstance]]:
    def decorator(cls: type[DataclassInstance]) -> type[DataclassInstance]:
        if not is_dataclass(cls):
            msg = f"{cls.__name__} must be a dataclass"
            raise TypeError(msg)

        ctx = _PatchContext(
            loader_instance=loader_instance,
            file_path=file_path,
            cls=cls,
            metadata=metadata,
            cache=cache,
            debug=debug,
        )
        cls.__init__ = _make_new_init(ctx)  # type: ignore[method-assign]
        cls.__post_init__ = _make_new_post_init(ctx)  # type: ignore[attr-defined]
        return cls

    return decorator
