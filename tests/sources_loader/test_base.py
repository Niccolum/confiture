"""Tests for base module (ILoader base class)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.base import ILoader
from dature.types import JSONValue


class MockLoader(ILoader):
    """Mock loader for testing base class functionality."""

    def __init__(self, prefix: str | None = None, test_data: JSONValue = None):
        super().__init__(prefix=prefix)
        self._test_data = test_data or {}

    def _load(self, path: Path) -> JSONValue:  # noqa: ARG002
        """Return test data."""
        return self._test_data


class TestILoaderBase:
    """Tests for ILoader base class."""

    def test_apply_prefix_simple(self):
        """Test applying simple prefix."""
        data = {"app": {"name": "Test", "port": 8080}, "other": "value"}
        loader = MockLoader(prefix="app", test_data=data)

        result = loader._apply_prefix(data)

        assert result == {"name": "Test", "port": 8080}

    def test_apply_prefix_nested(self):
        """Test applying nested prefix with dots."""
        data = {"app": {"database": {"host": "localhost", "port": 5432}}}
        loader = MockLoader(prefix="app.database", test_data=data)

        result = loader._apply_prefix(data)

        assert result == {"host": "localhost", "port": 5432}

    def test_apply_prefix_none(self):
        """Test that None prefix returns original data."""
        data = {"key": "value"}
        loader = MockLoader(test_data=data)

        result = loader._apply_prefix(data)

        assert result == data

    def test_apply_prefix_empty_string(self):
        """Test that empty string prefix returns original data."""
        data = {"key": "value"}
        loader = MockLoader(prefix="", test_data=data)

        result = loader._apply_prefix(data)

        assert result == data

    def test_apply_prefix_nonexistent(self):
        """Test applying nonexistent prefix returns empty dict."""
        data = {"app": {"name": "Test"}}
        loader = MockLoader(prefix="nonexistent", test_data=data)

        result = loader._apply_prefix(data)

        assert result == {}

    def test_apply_prefix_deep_nesting(self):
        """Test applying deeply nested prefix."""
        data = {"a": {"b": {"c": {"d": {"value": "deep"}}}}}
        loader = MockLoader(prefix="a.b.c.d", test_data=data)

        result = loader._apply_prefix(data)

        assert result == {"value": "deep"}

    def test_apply_prefix_invalid_path(self):
        """Test applying prefix with invalid path."""
        data = {"app": "not_a_dict"}
        loader = MockLoader(prefix="app.nested", test_data=data)

        result = loader._apply_prefix(data)

        assert result == {}

    def test_transform_to_dataclass(self):
        """Test transformation of data to dataclass."""

        @dataclass
        class Config:
            name: str
            port: int

        expected_data = Config(name="TestApp", port=8080)
        data = {"name": "TestApp", "port": 8080}
        loader = MockLoader(test_data=data)

        result = loader._transform_to_dataclass(data, Config)

        assert result == expected_data

    def test_transform_to_dataclass_with_nested(self):
        """Test transformation with nested dataclass."""

        @dataclass
        class DatabaseConfig:
            host: str
            port: int

        @dataclass
        class Config:
            database: DatabaseConfig

        expected_data = Config(database=DatabaseConfig(host="localhost", port=5432))
        data = {"database": {"host": "localhost", "port": 5432}}
        loader = MockLoader(test_data=data)

        result = loader._transform_to_dataclass(data, Config)

        assert result == expected_data

    def test_load_full_pipeline(self):
        """Test full load pipeline."""

        @dataclass
        class Config:
            name: str
            port: int
            debug: bool
            default: str = "value"

        expected_data = Config(name="TestApp", port=8080, debug=True, default="value")
        data = {"app": {"name": "TestApp", "port": 8080, "debug": "true"}}
        loader = MockLoader(prefix="app", test_data=data)

        result = loader.load(Path(), Config)

        assert result == expected_data

    def test_apply_prefix_with_list(self):
        """Test that apply_prefix returns data as-is when prefix points to non-dict."""
        data = {"items": [1, 2, 3]}
        loader = MockLoader(prefix="items", test_data=data)

        result = loader._apply_prefix(data)

        assert result == [1, 2, 3]
