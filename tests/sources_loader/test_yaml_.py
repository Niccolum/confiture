"""Tests for yaml_ module (YamlLoader)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.yaml_ import YamlLoader
from tests.sources_loader.all_types_dataclass import EXPECTED_ALL_TYPES, AllPythonTypesCompact


class TestYamlLoader:
    """Tests for YamlLoader class."""

    def test_comprehensive_type_conversion(self, all_types_yaml_file: Path):
        """Test loading YAML with full type coercion to dataclass."""
        loader = YamlLoader()
        result = loader.load(all_types_yaml_file, AllPythonTypesCompact)

        assert result == EXPECTED_ALL_TYPES

    def test_yaml_with_prefix(self, prefixed_yaml_file: Path):
        @dataclass
        class PrefixedConfig:
            name: str
            port: int
            debug: bool
            environment: str

        expected_data = PrefixedConfig(
            name="PrefixedApp",
            port=9000,
            debug=False,
            environment="production",
        )
        loader = YamlLoader(prefix="app")

        result = loader.load(prefixed_yaml_file, PrefixedConfig)

        assert result == expected_data

    def test_yaml_env_var_substitution(self, yaml_config_with_env_vars_file: Path, monkeypatch):
        """Test YAML environment variable substitution."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/db")
        monkeypatch.setenv("SECRET_KEY", "my_secret")
        monkeypatch.setenv("REDIS_HOST", "redis.local")
        monkeypatch.setenv("QUEUE_HOST", "queue.local")
        expected_data = {
            "database_url": "postgresql://localhost/db",
            "secret_key": "my_secret",
            "services": {
                "cache": {"host": "redis.local"},
                "queue": {"host": "queue.local"},
            },
        }

        loader = YamlLoader()
        data = loader._load(yaml_config_with_env_vars_file)

        assert data == expected_data

    def test_yaml_empty_file(self, tmp_path: Path):
        """Test loading empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        loader = YamlLoader()
        data = loader._load(yaml_file)

        assert data is None
