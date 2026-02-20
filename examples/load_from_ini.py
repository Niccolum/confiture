"""dature.load() with explicit loader="ini" and prefix for section selection."""

from dataclasses import dataclass
from pathlib import Path

from dature import LoadMetadata, load

SOURCES_DIR = Path(__file__).parent / "sources"


@dataclass
class ServerConfig:
    host: str
    port: int
    debug: bool
    workers: int


config = load(
    LoadMetadata(file_=str(SOURCES_DIR / "server.ini"), loader="ini", prefix="server"),
    ServerConfig,
)

print(f"host: {config.host}")
print(f"port: {config.port}")
print(f"debug: {config.debug}")
print(f"workers: {config.workers}")
