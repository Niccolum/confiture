"""Tests for INI-specific loader functions."""

import pytest

from dature.sources_loader.loaders.ini_ import dict_from_json_string


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ('{"key":"value"}', {"key": "value"}),
        ("", {}),
        ('{1: "one", 2: "two"}', {1: "one", 2: "two"}),
    ],
)
def test_dict_from_json_string(input_value, expected):
    assert dict_from_json_string(input_value) == expected
