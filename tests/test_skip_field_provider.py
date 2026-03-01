"""Tests for skip_field_provider.py."""

from dataclasses import dataclass

from adaptix import Retort

from dature.skip_field_provider import (
    ModelToDictProvider,
    SkipFieldProvider,
    filter_invalid_fields,
)


class TestFilterInvalidFields:
    def test_all_fields_valid(self):
        @dataclass
        class Config:
            host: str
            port: int

        probe = Retort(
            strict_coercion=False,
            recipe=[SkipFieldProvider(), ModelToDictProvider()],
        )
        raw = {"host": "localhost", "port": 8080}
        result = filter_invalid_fields(raw, probe, Config, None)

        assert result.cleaned_dict == {"host": "localhost", "port": 8080}
        assert result.skipped_paths == []

    def test_one_field_invalid(self):
        @dataclass
        class Config:
            host: str
            port: int

        probe = Retort(
            strict_coercion=False,
            recipe=[SkipFieldProvider(), ModelToDictProvider()],
        )
        raw = {"host": "localhost", "port": "abc"}
        result = filter_invalid_fields(raw, probe, Config, None)

        assert result.cleaned_dict == {"host": "localhost"}
        assert result.skipped_paths == ["port"]

    def test_nested_field_invalid(self):
        @dataclass
        class Database:
            host: str
            port: int

        @dataclass
        class Config:
            db: Database

        probe = Retort(
            strict_coercion=False,
            recipe=[SkipFieldProvider(), ModelToDictProvider()],
        )
        raw = {"db": {"host": "localhost", "port": "abc"}}
        result = filter_invalid_fields(raw, probe, Config, None)

        assert result.cleaned_dict == {"db": {"host": "localhost"}}
        assert result.skipped_paths == ["db.port"]

    def test_allowed_fields_restricts_skip(self):
        @dataclass
        class Config:
            host: str
            port: int
            timeout: int

        probe = Retort(
            strict_coercion=False,
            recipe=[SkipFieldProvider(), ModelToDictProvider()],
        )
        raw = {"host": "localhost", "port": "abc", "timeout": "bad"}
        result = filter_invalid_fields(raw, probe, Config, {"port"})

        assert result.cleaned_dict == {"host": "localhost", "timeout": "bad"}
        assert result.skipped_paths == ["port"]

    def test_non_dict_input(self):
        @dataclass
        class Config:
            host: str

        probe = Retort(
            strict_coercion=False,
            recipe=[SkipFieldProvider(), ModelToDictProvider()],
        )
        result = filter_invalid_fields("not a dict", probe, Config, None)

        assert result.cleaned_dict == "not a dict"
        assert result.skipped_paths == []
