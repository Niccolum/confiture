"""Tests for ENV-specific loader functions."""

import pytest

from dature.sources_loader.loaders.env_ import dict_from_env_nested


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        # JSON string case
        ('{"key": "value"}', {"key": "value"}),
        ("", {}),
        # Nested dict with string values
        ({"host": "localhost", "port": "5432"}, {"host": "localhost", "port": 5432}),
        ({"string": "text", "number": "42", "float": "3.14"}, {"string": "text", "number": 42, "float": 3.14}),
        # Nested dict with recursive structure
        ({"db": {"host": "localhost", "port": "5432"}}, {"db": {"host": "localhost", "port": 5432}}),
        # Numeric keys
        ({"1": "one", "2": "two"}, {1: "one", 2: "two"}),
        # Boolean values
        ({"enabled": "true"}, {"enabled": True}),
        ({"enabled": "True"}, {"enabled": True}),
        ({"enabled": "TRUE"}, {"enabled": True}),
        ({"enabled": "1"}, {"enabled": True}),
        ({"enabled": "yes"}, {"enabled": True}),
        ({"enabled": "Yes"}, {"enabled": True}),
        ({"enabled": "on"}, {"enabled": True}),
        ({"enabled": "ON"}, {"enabled": True}),
        ({"enabled": "false"}, {"enabled": False}),
        ({"enabled": "False"}, {"enabled": False}),
        ({"enabled": "FALSE"}, {"enabled": False}),
        ({"enabled": "0"}, {"enabled": False}),
        ({"enabled": "no"}, {"enabled": False}),
        ({"enabled": "No"}, {"enabled": False}),
        ({"enabled": "off"}, {"enabled": False}),
        ({"enabled": "OFF"}, {"enabled": False}),
    ],
)
def test_dict_from_env_nested(input_value, expected):
    assert dict_from_env_nested(input_value) == expected
