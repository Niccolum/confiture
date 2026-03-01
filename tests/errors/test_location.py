from pathlib import Path

from dature.errors.exceptions import LineRange
from dature.errors.location import ErrorContext, resolve_source_location
from dature.path_finders.json_ import JsonPathFinder
from dature.path_finders.toml_ import Toml11PathFinder


class TestResolveSourceLocation:
    def test_env_source(self):
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="env",
            file_path=None,
            prefix="APP_",
            split_symbols="__",
            path_finder_class=None,
        )
        loc = resolve_source_location(["database", "port"], ctx, file_content=None)
        assert loc.source_type == "env"
        assert loc.env_var_name == "APP_DATABASE__PORT"
        assert loc.file_path is None

    def test_env_source_no_prefix(self):
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="env",
            file_path=None,
            prefix=None,
            split_symbols="__",
            path_finder_class=None,
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=None)
        assert loc.env_var_name == "TIMEOUT"

    def test_env_source_custom_split_symbols(self):
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="env",
            file_path=None,
            prefix="APP_",
            split_symbols="_",
            path_finder_class=None,
        )
        loc = resolve_source_location(["database", "port"], ctx, file_content=None)
        assert loc.env_var_name == "APP_DATABASE_PORT"

    def test_json_source_with_line(self):
        content = '{\n  "timeout": "30",\n  "name": "test"\n}'
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="json",
            file_path=Path("config.json"),
            prefix=None,
            split_symbols="__",
            path_finder_class=JsonPathFinder,
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=content)
        assert loc.source_type == "json"
        assert loc.line_range == LineRange(start=2, end=2)
        assert loc.line_content == ['"timeout": "30",']

    def test_toml_source_with_line(self):
        content = 'timeout = "30"\nname = "test"'
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="toml",
            file_path=Path("config.toml"),
            prefix=None,
            split_symbols="__",
            path_finder_class=Toml11PathFinder,
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=content)
        assert loc.source_type == "toml"
        assert loc.line_range == LineRange(start=1, end=1)
        assert loc.line_content == ['timeout = "30"']

    def test_envfile_source(self):
        content = "# comment\nAPP_TIMEOUT=30\nAPP_NAME=test"
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="envfile",
            file_path=Path(".env"),
            prefix="APP_",
            split_symbols="__",
            path_finder_class=None,
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=content)
        assert loc.source_type == "envfile"
        assert loc.env_var_name == "APP_TIMEOUT"
        assert loc.line_range == LineRange(start=2, end=2)
        assert loc.line_content == ["APP_TIMEOUT=30"]

    def test_file_source_does_not_mask_non_secret_field(self):
        content = '{\n  "password": "secret123",\n  "timeout": "30"\n}'
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="json",
            file_path=Path("config.json"),
            prefix=None,
            split_symbols="__",
            path_finder_class=JsonPathFinder,
            secret_paths=frozenset({"password"}),
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=content)
        assert loc.line_content == ['"timeout": "30"']

    def test_file_source_masks_secret_field(self):
        content = '{\n  "password": "secret123",\n  "timeout": "30"\n}'
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="json",
            file_path=Path("config.json"),
            prefix=None,
            split_symbols="__",
            path_finder_class=JsonPathFinder,
            secret_paths=frozenset({"password"}),
        )
        loc = resolve_source_location(["password"], ctx, file_content=content)
        assert loc.line_content == ['"password": "se*****23",']

    def test_file_source_masks_line_when_secret_on_same_line(self):
        content = '{"password": "secret123", "timeout": "30"}'
        ctx = ErrorContext(
            dataclass_name="Config",
            loader_type="json",
            file_path=Path("config.json"),
            prefix=None,
            split_symbols="__",
            path_finder_class=JsonPathFinder,
            secret_paths=frozenset({"password"}),
        )
        loc = resolve_source_location(["timeout"], ctx, file_content=content)
        assert loc.line_content == ['{"password": "se*****23", "timeout": "30"}']
