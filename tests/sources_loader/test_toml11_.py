"""Tests for toml_ module (Toml11Loader)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.toml_ import Toml11Loader
from examples.all_types_dataclass import (
    EXPECTED_ALL_TYPES,
    AllPythonTypesCompact,
)
from tests.sources_loader.checker import assert_all_types_equal


class TestToml11Loader:
    """Tests for Toml11Loader class."""

    def test_comprehensive_type_conversion(self, all_types_toml11_file: Path):
        """Test loading TOML with full type coercion to dataclass."""
        loader = Toml11Loader()
        result = loader.load(all_types_toml11_file, AllPythonTypesCompact)

        assert_all_types_equal(result, EXPECTED_ALL_TYPES)

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
        loader = Toml11Loader(prefix="app")

        result = loader.load(prefixed_toml_file, PrefixedConfig)

        assert result == expected_data

    def test_toml_empty_file(self, tmp_path: Path):
        """Test loading empty TOML file."""
        toml_file = tmp_path / "empty.toml"
        toml_file.write_text("")

        loader = Toml11Loader()
        data = loader._load(toml_file)

        assert data == {}

    def test_toml_env_var_substitution(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("APP_NAME", "MyApp")
        monkeypatch.setenv("APP_PORT", "9090")

        toml_file = tmp_path / "env.toml"
        toml_file.write_text('name = "$APP_NAME"\nport = "$APP_PORT"')

        @dataclass
        class Config:
            name: str
            port: int

        loader = Toml11Loader()
        result = loader.load(toml_file, Config)

        assert result.name == "MyApp"
        assert result.port == 9090

    def test_toml_env_var_partial_substitution(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "8080")

        toml_file = tmp_path / "env.toml"
        toml_file.write_text('url = "http://${HOST}:${PORT}/api"')

        @dataclass
        class Config:
            url: str

        loader = Toml11Loader()
        result = loader.load(toml_file, Config)

        assert result.url == "http://localhost:8080/api"

    def test_toml_dollar_sign_mid_string_existing_var(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("abc", "replaced")

        toml_file = tmp_path / "dollar.toml"
        toml_file.write_text('value = "prefix$abc/suffix"')

        @dataclass
        class Config:
            value: str

        loader = Toml11Loader()
        result = loader.load(toml_file, Config)

        assert result.value == "prefixreplaced/suffix"

    def test_toml_dollar_sign_mid_string_missing_var(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv("nonexistent", raising=False)

        toml_file = tmp_path / "dollar.toml"
        toml_file.write_text('value = "prefix$nonexistent/suffix"')

        @dataclass
        class Config:
            value: str

        loader = Toml11Loader()
        result = loader.load(toml_file, Config)

        assert result.value == "prefix$nonexistent/suffix"
