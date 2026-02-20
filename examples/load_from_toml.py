"""Merge multiple sources — tuple-shorthand, LAST_WINS strategy."""

from dataclasses import dataclass
from pathlib import Path

from dature import LoadMetadata, load

SOURCES_DIR = Path(__file__).parent / "sources"

DEFAULTS = LoadMetadata(file_=str(SOURCES_DIR / "defaults.toml"))
OVERRIDES = LoadMetadata(file_=str(SOURCES_DIR / "overrides.toml"))


@dataclass
class Config:
    host: str
    port: int
    debug: bool
    workers: int
    tags: list[str]


config = load((DEFAULTS, OVERRIDES), Config)

print(f"host: {config.host}")
print(f"port: {config.port}")
print(f"debug: {config.debug}")
print(f"workers: {config.workers}")
print(f"tags: {config.tags}")
