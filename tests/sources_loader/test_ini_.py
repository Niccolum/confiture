"""Tests for ini_ module (IniLoader)."""

import configparser
from dataclasses import dataclass
from pathlib import Path

import pytest

from dature.sources_loader.ini_ import IniLoader
from tests.sources_loader.all_types_dataclass import EXPECTED_ALL_TYPES, AllPythonTypesCompact


class TestIniLoader:
    """Tests for IniLoader class."""

    def test_comprehensive_type_conversion(self, all_types_ini_file: Path):
        """Test loading INI with full type coercion to dataclass."""
        loader = IniLoader(prefix="all_types")
        result = loader.load(all_types_ini_file, AllPythonTypesCompact)

        assert result == EXPECTED_ALL_TYPES

    def test_ini_sections(self, ini_sections_file: Path):
        """Test INI sections and DEFAULT inheritance."""
        loader = IniLoader()
        data = loader._load(ini_sections_file)

        assert data == {
            "DEFAULT": {
                "app_name": "TestApp",
            },
            "app": {
                "app_name": "MyApp",
                "port": "8080",
            },
            "database": {
                "host": "localhost",
                "app_name": "TestApp",
            },
        }

    def test_ini_with_prefix(self, prefixed_ini_file: Path):
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
        loader = IniLoader(prefix="app")
        result = loader.load(prefixed_ini_file, PrefixedConfig)

        assert result == expected_data

    def test_ini_requires_sections(self, tmp_path: Path):
        """Test that INI format requires section headers."""
        ini_file = tmp_path / "nosection.ini"
        ini_file.write_text("key = value")

        loader = IniLoader()

        with pytest.raises(configparser.MissingSectionHeaderError):
            loader._load(ini_file)
