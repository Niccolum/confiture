"""Tests for base loader functions (used only in ILoader defaults)."""

from datetime import timedelta
from urllib.parse import urlparse

import pytest

from dature.sources_loader.loaders.base import (
    bytes_from_string,
    complex_from_string,
    timedelta_from_string,
    url_from_string,
)


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


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("2:30:00", timedelta(hours=2, minutes=30)),
        ("0:00:01", timedelta(seconds=1)),
        ("0:45:00", timedelta(minutes=45)),
        ("1 day, 2:30:00", timedelta(days=1, hours=2, minutes=30)),
        ("2 days, 0:00:00", timedelta(days=2)),
        ("1 day, 2:03:04.500000", timedelta(days=1, hours=2, minutes=3, seconds=4, microseconds=500000)),
        ("-1 day, 23:59:59", timedelta(days=-1, hours=23, minutes=59, seconds=59)),
        ("-2 days, 23:59:59", timedelta(days=-2, hours=23, minutes=59, seconds=59)),
    ],
)
def test_timedelta_from_string(input_value: str, expected: timedelta):
    assert timedelta_from_string(input_value) == expected


def test_timedelta_from_string_invalid():
    with pytest.raises(ValueError, match="Invalid timedelta format"):
        timedelta_from_string("not a timedelta")


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        (
            "https://example.com/path?query=value#fragment",
            urlparse("https://example.com/path?query=value#fragment"),
        ),
        (
            "http://localhost:8080",
            urlparse("http://localhost:8080"),
        ),
        (
            "ftp://files.example.com/data.csv",
            urlparse("ftp://files.example.com/data.csv"),
        ),
    ],
)
def test_url_from_string(input_value: str, expected):
    assert url_from_string(input_value) == expected
