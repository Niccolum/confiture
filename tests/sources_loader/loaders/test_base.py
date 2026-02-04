"""Tests for base loader functions (used only in ILoader defaults)."""

import pytest

from dature.sources_loader.loaders.base import bytes_from_string, complex_from_string


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("hello", b"hello"),
    ],
)
def test_bytes_from_string(input_value, expected):
    assert bytes_from_string(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("1+2j", 1 + 2j),
    ],
)
def test_complex_from_string(input_value, expected):
    assert complex_from_string(input_value) == expected
