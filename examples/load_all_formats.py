"""dature.load() as a function — auto-detect format by file extension."""

from pathlib import Path

from all_types_dataclass import AllPythonTypesCompact  # type: ignore[import-not-found]

from dature import LoadMetadata, load

SOURCES_DIR = Path(__file__).parent / "sources"

FORMATS = {
    "json": LoadMetadata(file_=str(SOURCES_DIR / "all_types.json")),
    "json5": LoadMetadata(file_=str(SOURCES_DIR / "all_types.json5")),
    "toml": LoadMetadata(file_=str(SOURCES_DIR / "all_types.toml")),
    "ini": LoadMetadata(file_=str(SOURCES_DIR / "all_types.ini"), prefix="all_types"),
    "yaml11": LoadMetadata(file_=str(SOURCES_DIR / "all_types_yaml11.yaml"), loader="yaml1.1"),
    "yaml12": LoadMetadata(file_=str(SOURCES_DIR / "all_types_yaml12.yaml"), loader="yaml1.2"),
    "env": LoadMetadata(file_=str(SOURCES_DIR / "all_types.env")),
}

for name, meta in FORMATS.items():
    config = load(meta, AllPythonTypesCompact)
    print(f"[{name}] string_value={config.string_value}, integer_value={config.integer_value}")
    print(f"[{name}] string_value={config.string_value}, integer_value={config.integer_value}")
