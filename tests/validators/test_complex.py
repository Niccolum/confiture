from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import pytest
from adaptix.load_error import AggregateLoadError, ValidationLoadError

from dature import LoadMetadata, load
from dature.validators.number import Ge, Le
from dature.validators.sequence import MinItems, UniqueItems
from dature.validators.string import MaxLength, MinLength, RegexPattern


class TestMultipleFields:
    def test_success(self, tmp_path: Path):
        @dataclass
        class Config:
            name: Annotated[str, MinLength(value=3), MaxLength(value=50)]
            age: Annotated[int, Ge(value=0), Le(value=150)]
            tags: Annotated[list[str], MinItems(value=1), UniqueItems()]

        json_file = tmp_path / "config.json"
        json_file.write_text('{"name": "Alice", "age": 30, "tags": ["python", "coding"]}')

        metadata = LoadMetadata(file_=str(json_file))
        result = load(metadata, Config)

        assert result.name == "Alice"
        assert result.age == 30
        assert result.tags == ["python", "coding"]

    def test_all_invalid(self, tmp_path: Path):
        @dataclass
        class Config:
            name: Annotated[str, MinLength(value=3), MaxLength(value=50)]
            age: Annotated[int, Ge(value=0), Le(value=150)]
            tags: Annotated[list[str], MinItems(value=1), UniqueItems()]

        json_file = tmp_path / "config.json"
        json_file.write_text('{"name": "AB", "age": 200, "tags": []}')

        metadata = LoadMetadata(file_=str(json_file))

        with pytest.raises(AggregateLoadError) as exc_info:
            load(metadata, Config)

        e = exc_info.value
        assert len(e.exceptions) == 3
        for exc in e.exceptions:
            assert isinstance(exc, ValidationLoadError)

        error_messages = [exc.msg for exc in e.exceptions]
        assert "Value must have at least 3 characters" in error_messages
        assert "Value must be less than or equal to 150" in error_messages
        assert "Value must have at least 1 items" in error_messages


class TestNestedDataclass:
    def test_success(self, tmp_path: Path):
        @dataclass
        class Address:
            city: Annotated[str, MinLength(value=2)]
            zip_code: Annotated[str, RegexPattern(pattern=r"^\d{5}$")]

        @dataclass
        class User:
            name: Annotated[str, MinLength(value=3)]
            age: Annotated[int, Ge(value=18)]
            address: Address

        json_file = tmp_path / "config.json"
        json_file.write_text(
            '{"name": "Alice", "age": 30, "address": {"city": "NYC", "zip_code": "12345"}}',
        )

        metadata = LoadMetadata(file_=str(json_file))
        result = load(metadata, User)

        assert result.name == "Alice"
        assert result.age == 30
        assert result.address.city == "NYC"
        assert result.address.zip_code == "12345"

    def test_all_invalid(self, tmp_path: Path):
        @dataclass
        class Address:
            city: Annotated[str, MinLength(value=2)]
            zip_code: Annotated[str, RegexPattern(pattern=r"^\d{5}$")]

        @dataclass
        class User:
            name: Annotated[str, MinLength(value=3)]
            age: Annotated[int, Ge(value=18)]
            address: Address

        json_file = tmp_path / "config.json"
        json_file.write_text(
            '{"name": "Al", "age": 15, "address": {"city": "N", "zip_code": "ABCDE"}}',
        )

        metadata = LoadMetadata(file_=str(json_file))

        with pytest.raises(AggregateLoadError) as exc_info:
            load(metadata, User)

        def collect_validation_errors(exc: BaseException, errors: list[ValidationLoadError]) -> None:
            if isinstance(exc, ValidationLoadError):
                errors.append(exc)
            if hasattr(exc, "exceptions"):
                for sub_exc in exc.exceptions:
                    collect_validation_errors(sub_exc, errors)

        validation_errors: list[ValidationLoadError] = []
        collect_validation_errors(exc_info.value, validation_errors)

        assert len(validation_errors) == 4

        error_messages = [e.msg for e in validation_errors]
        assert "Value must have at least 3 characters" in error_messages
        assert "Value must be greater than or equal to 18" in error_messages
        assert "Value must have at least 2 characters" in error_messages
        assert any("must match pattern" in msg for msg in error_messages if msg is not None)


class TestCustomErrorMessage:
    def test_custom_error_message(self, tmp_path: Path):
        @dataclass
        class Config:
            age: Annotated[int, Ge(value=18, error_message="Age must be 18 or older")]

        json_file = tmp_path / "config.json"
        json_file.write_text('{"age": 15}')

        metadata = LoadMetadata(file_=str(json_file))

        with pytest.raises(AggregateLoadError) as exc_info:
            load(metadata, Config)

        e = exc_info.value
        assert len(e.exceptions) == 1
        assert isinstance(e.exceptions[0], ValidationLoadError)
        assert e.exceptions[0].msg == "Age must be 18 or older"
