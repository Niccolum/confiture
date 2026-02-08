"""Tests for json_ module (JsonLoader)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.json_ import JsonLoader
from tests.sources_loader.all_types_dataclass import (
    EXPECTED_ALL_TYPES,
    AllPythonTypesCompact,
    assert_all_types_equal,
)


class TestJsonLoader:
    """Tests for JsonLoader class."""

    def test_comprehensive_type_conversion(self, all_types_json_file: Path):
        """Test loading JSON with full type coercion to dataclass."""
        loader = JsonLoader()
        result = loader.load(all_types_json_file, AllPythonTypesCompact)

        assert_all_types_equal(result, EXPECTED_ALL_TYPES)

    def test_json_with_prefix(self, prefixed_json_file: Path):
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
        loader = JsonLoader(prefix="app")

        result = loader.load(prefixed_json_file, PrefixedConfig)

        assert result == expected_data

    def test_json_empty_object(self, tmp_path: Path):
        """Test loading empty JSON object."""
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")

        loader = JsonLoader()
        data = loader._load(json_file)

        assert data == {}
