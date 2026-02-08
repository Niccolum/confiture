"""Tests for env_ module (EnvLoader and EnvFileLoader)."""

from dataclasses import dataclass
from pathlib import Path

from dature.sources_loader.env_ import EnvFileLoader, EnvLoader
from tests.sources_loader.all_types_dataclass import EXPECTED_ALL_TYPES, AllPythonTypesCompact


class TestEnvFileLoader:
    """Tests for EnvFileLoader class."""

    def test_prefix_filtering(self, prefixed_env_file: Path):
        """Test prefix filtering with nested structures."""
        loader = EnvFileLoader(prefix="APP_")
        data = loader._load(prefixed_env_file)

        assert data == {
            "name": "PrefixedApp",
            "environment": "production",
            "database": {
                "host": "prod.db.com",
                "port": "5432",
            },
        }

    def test_custom_split_symbols(self, custom_separator_env_file: Path):
        """Test custom separator for nested keys."""
        loader = EnvFileLoader(prefix="APP_", split_symbols=".")
        data = loader._load(custom_separator_env_file)

        assert data == {
            "name": "CustomApp",
            "environment": "development",
            "db": {
                "host": "dev.db.com",
                "port": "5432",
            },
        }

    def test_comprehensive_type_conversion(self, all_types_env_file: Path):
        """Test loading ENV with full type coercion to dataclass."""
        loader = EnvFileLoader()
        result = loader.load(all_types_env_file, AllPythonTypesCompact)

        assert result == EXPECTED_ALL_TYPES

    def test_empty_file(self, tmp_path: Path):
        """Test loading empty .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        loader = EnvFileLoader()
        data = loader._load(env_file)

        assert data == {}


class TestEnvLoader:
    """Tests for EnvLoader class."""

    def test_comprehensive_type_conversion(self, monkeypatch):
        """Test loading from os.environ with full type coercion to dataclass."""
        # Set all environment variables
        monkeypatch.setenv("APP_STRING_VALUE", "hello world")
        monkeypatch.setenv("APP_INTEGER_VALUE", "42")
        monkeypatch.setenv("APP_FLOAT_VALUE", "3.14159")
        monkeypatch.setenv("APP_BOOLEAN_VALUE", "true")
        monkeypatch.setenv("APP_NONE_VALUE", "")

        # Lists (JSON format)
        monkeypatch.setenv("APP_LIST_STRINGS", '["item1","item2","item3"]')
        monkeypatch.setenv("APP_LIST_INTEGERS", "[1,2,3,4,5]")
        monkeypatch.setenv("APP_LIST_MIXED", '["string",42,3.14,true,null]')
        monkeypatch.setenv("APP_LIST_NESTED", '[["a","b"],["c","d"]]')
        monkeypatch.setenv("APP_LIST_DICTS", '[{"name":"Alice","age":30},{"name":"Bob","age":25}]')

        # Tuples (JSON arrays)
        monkeypatch.setenv("APP_TUPLE_SIMPLE", "[1,2,3]")
        monkeypatch.setenv("APP_TUPLE_MIXED", '["text",42,true]')
        monkeypatch.setenv("APP_TUPLE_NESTED", '[[1,2,3],["a","b","c"]]')

        # Sets (JSON arrays)
        monkeypatch.setenv("APP_SET_INTEGERS", "[1,2,3,4,5]")
        monkeypatch.setenv("APP_SET_STRINGS", '["apple","banana","cherry"]')

        # Dictionaries (__ notation)
        monkeypatch.setenv("APP_DICT_SIMPLE__KEY1", "value1")
        monkeypatch.setenv("APP_DICT_SIMPLE__KEY2", "value2")
        monkeypatch.setenv("APP_DICT_MIXED__STRING", "text")
        monkeypatch.setenv("APP_DICT_MIXED__NUMBER", "42")
        monkeypatch.setenv("APP_DICT_MIXED__FLOAT", "3.14")
        monkeypatch.setenv("APP_DICT_MIXED__BOOL", "true")
        monkeypatch.setenv("APP_DICT_MIXED__LIST", "[1,2,3]")
        monkeypatch.setenv("APP_DICT_NESTED__LEVEL1__LEVEL2__LEVEL3", "deep_value")
        monkeypatch.setenv("APP_DICT_INT_KEYS__1", "one")
        monkeypatch.setenv("APP_DICT_INT_KEYS__2", "two")
        monkeypatch.setenv("APP_DICT_INT_KEYS__3", "three")
        monkeypatch.setenv(
            "APP_DICT_LIST_DICT",
            '{"users":[{"name":"Alice","role":"admin"},{"name":"Bob","role":"user"}],"teams":[{"name":"backend","size":5}]}',
        )

        # Special types
        monkeypatch.setenv("APP_DATE_VALUE", "2024-01-15")
        monkeypatch.setenv("APP_DATETIME_VALUE", "2024-01-15T10:30:00")
        monkeypatch.setenv("APP_DATETIME_VALUE_WITH_TIMEZONE", "2024-01-15T10:30:00+03:00")
        monkeypatch.setenv("APP_DATETIME_VALUE_WITH_Z_TIMEZONE", "2024-01-15T10:30:00Z")
        monkeypatch.setenv("APP_TIME_VALUE", "10:30:00")
        monkeypatch.setenv("APP_BYTES_VALUE", "binary data")
        monkeypatch.setenv("APP_BYTEARRAY_VALUE", "binary")
        monkeypatch.setenv("APP_COMPLEX_VALUE", "1+2j")

        # Edge cases
        monkeypatch.setenv("APP_EMPTY_STRING", "")
        monkeypatch.setenv("APP_EMPTY_LIST", "[]")
        monkeypatch.setenv("APP_EMPTY_DICT", "{}")
        monkeypatch.setenv("APP_ZERO_INT", "0")
        monkeypatch.setenv("APP_ZERO_FLOAT", "0.0")
        monkeypatch.setenv("APP_FALSE_BOOL", "false")

        # Advanced patterns
        monkeypatch.setenv("APP_OPTIONAL_STRING", "")
        monkeypatch.setenv("APP_UNION_TYPE", "42")
        monkeypatch.setenv(
            "APP_NESTED_OPTIONAL",
            '[{"name":"Alice","email":"alice@example.com"},{"name":"Bob","email":null}]',
        )
        monkeypatch.setenv("APP_RANGE_VALUES", "[0,2,4,6,8]")
        monkeypatch.setenv("APP_FROZENSET_VALUE", "[1,2,3,4,5]")

        loader = EnvLoader(prefix="APP_")
        result = loader.load(Path(), AllPythonTypesCompact)

        assert result == EXPECTED_ALL_TYPES

    def test_prefix_filtering(self, monkeypatch):
        """Test that only variables with prefix are loaded."""
        monkeypatch.setenv("APP_VAR", "included")
        monkeypatch.setenv("OTHER_VAR", "excluded")
        monkeypatch.setenv("APP_KEY", "also_included")

        @dataclass
        class TestConfig:
            var: str
            key: str

        expected_data = TestConfig(var="included", key="also_included")

        loader = EnvLoader(prefix="APP_")
        data = loader.load(Path(), TestConfig)

        assert data == expected_data

    def test_custom_split_symbols(self, monkeypatch):
        """Test custom separator for nested keys."""
        monkeypatch.setenv("APP_DB.HOST", "localhost")
        monkeypatch.setenv("APP_DB.PORT", "5432")

        @dataclass
        class TestData:
            host: str
            port: str

        @dataclass
        class TestConfig:
            db: TestData

        expected_data = TestConfig(db=TestData(host="localhost", port="5432"))

        loader = EnvLoader(prefix="APP_", split_symbols=".")
        data = loader.load(Path(), TestConfig)

        assert data == expected_data
