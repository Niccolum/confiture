"""Tests for toml_ module (TomlLoader)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.toml_ import TomlLoader
from tests.sources_loader.all_types_dataclass import EXPECTED_ALL_TYPES, AllPythonTypesCompact


class TestTomlLoader:
    """Tests for TomlLoader class."""

    def test_comprehensive_type_conversion(self, all_types_toml_file: Path):
        """Test loading TOML with full type coercion to dataclass."""
        loader = TomlLoader()
        result = loader.load(all_types_toml_file, AllPythonTypesCompact)

        assert result == EXPECTED_ALL_TYPES

    def test_toml_with_prefix(self, prefixed_toml_file: Path):
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
        loader = TomlLoader(prefix="app")

        result = loader.load(prefixed_toml_file, PrefixedConfig)

        assert result == expected_data

    def test_toml_empty_file(self, tmp_path: Path):
        """Test loading empty TOML file."""
        toml_file = tmp_path / "empty.toml"
        toml_file.write_text("")

        loader = TomlLoader()
        data = loader._load(toml_file)

        assert data == {}
