from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dature.main import LoaderType
    from dature.types import DotSeparatedPath, FieldMapping, NameStyle


@dataclass(frozen=True, slots=True, kw_only=True)
class LoadMetadata:
    file_: str | None = None
    loader: "LoaderType | None" = None
    prefix: "DotSeparatedPath | None" = None
    name_style: "NameStyle | None" = None
    field_mapping: "FieldMapping | None" = None
