"""Comprehensive dataclass with all Python basic types without repetition."""

import math
from dataclasses import dataclass, fields
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import urlparse
from uuid import UUID
from zoneinfo import ZoneInfo

from dature.types import URL, Base64UrlBytes, Base64UrlStr


@dataclass
class AllPythonTypesCompact:
    """
    Comprehensive dataclass containing all Python basic types.
    Each field demonstrates a unique type or pattern.
    """

    # Scalars
    string_value: str
    integer_value: int
    float_value: float
    boolean_value: bool
    none_value: None

    # Numeric
    decimal_value: Decimal
    float_inf: float
    float_nan: float

    # Date/time
    date_value: date
    datetime_value: datetime
    datetime_value_with_timezone: datetime
    datetime_value_with_z_timezone: datetime
    time_value: time
    timedelta_value_with_day: timedelta
    timedelta_value_without_day: timedelta

    # Lists
    list_strings: list[str]
    list_integers: list[int]
    list_mixed: list[Any]
    list_nested: list[list[str]]
    list_dicts: list[dict[str, Any]]

    # Tuples
    tuple_simple: tuple[int, int, int]
    tuple_mixed: tuple[str, int, bool]
    tuple_nested: tuple[tuple[int, ...], tuple[str, ...]]

    # Sets
    set_integers: set[int]
    set_strings: set[str]

    # Dicts
    dict_simple: dict[str, str]
    dict_mixed: dict[str, Any]
    dict_nested: dict[str, dict[str, Any]]
    dict_int_keys: dict[int, str]
    dict_list_dict: dict[str, list[dict[str, Any]]]

    # Binary/encoding
    bytes_value: bytes
    bytearray_value: bytearray
    complex_value: complex
    base64url_bytes_value: Base64UrlBytes
    base64url_str_value: Base64UrlStr

    # Paths
    path_value: Path
    pure_posix_path_value: PurePosixPath
    pure_windows_path_value: PureWindowsPath

    # Network
    ipv4_address_value: IPv4Address
    ipv6_address_value: IPv6Address
    ipv4_network_value: IPv4Network
    ipv6_network_value: IPv6Network
    ipv4_interface_value: IPv4Interface
    ipv6_interface_value: IPv6Interface

    # Identifiers
    uuid_value: UUID
    url_value: URL

    # Edge cases
    empty_string: str
    empty_list: list[Any]
    empty_dict: dict[str, Any]
    zero_int: int
    zero_float: float
    false_bool: bool

    # Union/optional
    optional_string: str | None
    union_type: int | float | str
    nested_optional: list[dict[str, str | None]]

    range_values: list[int]

    frozenset_value: frozenset[int] | None = None


EXPECTED_ALL_TYPES = AllPythonTypesCompact(
    # Scalars
    string_value="hello world",
    integer_value=42,
    float_value=3.14159,
    boolean_value=True,
    none_value=None,
    # Numeric
    decimal_value=Decimal("3.14159265358979323846264338327950288"),
    float_inf=float("inf"),
    float_nan=float("nan"),
    # Date/time
    date_value=date(2024, 1, 15),
    datetime_value=datetime(2024, 1, 15, 10, 30),
    datetime_value_with_timezone=datetime(2024, 1, 15, 10, 30, tzinfo=ZoneInfo("Europe/Moscow")),
    datetime_value_with_z_timezone=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
    time_value=time(10, 30),
    timedelta_value_with_day=timedelta(days=1, hours=2, minutes=30),
    timedelta_value_without_day=timedelta(hours=2, minutes=30),
    # Lists
    list_strings=["item1", "item2", "item3"],
    list_integers=[1, 2, 3, 4, 5],
    list_mixed=["string", 42, 3.14, True, None],
    list_nested=[["a", "b"], ["c", "d"]],
    list_dicts=[
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ],
    # Tuples
    tuple_simple=(1, 2, 3),
    tuple_mixed=("text", 42, True),
    tuple_nested=((1, 2, 3), ("a", "b", "c")),
    # Sets
    set_integers={1, 2, 3, 4, 5},
    set_strings={"apple", "banana", "cherry"},
    # Dicts
    dict_simple={"key1": "value1", "key2": "value2"},
    dict_mixed={
        "string": "text",
        "number": 42,
        "float": 3.14,
        "bool": True,
        "list": [1, 2, 3],
    },
    dict_nested={"level1": {"level2": {"level3": "deep_value"}}},
    dict_int_keys={1: "one", 2: "two", 3: "three"},
    dict_list_dict={
        "users": [
            {"name": "Alice", "role": "admin"},
            {"name": "Bob", "role": "user"},
        ],
        "teams": [
            {"name": "backend", "size": 5},
        ],
    },
    # Binary/encoding
    bytes_value=b"binary data",
    bytearray_value=bytearray(b"binary"),
    complex_value=1 + 2j,
    base64url_bytes_value=b"Hello World",
    base64url_str_value="secret token",
    # Paths
    path_value=Path("/usr/local/bin"),
    pure_posix_path_value=PurePosixPath("/etc/hosts"),
    pure_windows_path_value=PureWindowsPath("C:/Windows/System32"),
    # Network
    ipv4_address_value=IPv4Address("192.168.1.1"),
    ipv6_address_value=IPv6Address("2001:db8::1"),
    ipv4_network_value=IPv4Network("192.168.1.0/24"),
    ipv6_network_value=IPv6Network("2001:db8::/32"),
    ipv4_interface_value=IPv4Interface("192.168.1.1/24"),
    ipv6_interface_value=IPv6Interface("2001:db8::1/32"),
    # Identifiers
    uuid_value=UUID("550e8400-e29b-41d4-a716-446655440000"),
    url_value=urlparse("https://example.com/path?query=value#fragment"),
    # Edge cases
    empty_string="",
    empty_list=[],
    empty_dict={},
    zero_int=0,
    zero_float=0.0,
    false_bool=False,
    # Union/optional
    optional_string=None,
    union_type=42,
    nested_optional=[
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": None},
    ],
    range_values=[0, 2, 4, 6, 8],
    frozenset_value=frozenset({1, 2, 3, 4, 5}),
)


def assert_all_types_equal(result: AllPythonTypesCompact, expected: AllPythonTypesCompact) -> None:
    for field in fields(result):
        result_val = getattr(result, field.name)
        expected_val = getattr(expected, field.name)
        if (
            isinstance(result_val, float)
            and isinstance(expected_val, float)
            and math.isnan(result_val)
            and math.isnan(expected_val)
        ):
            continue
        assert result_val == expected_val, f"{field.name}: {result_val!r} != {expected_val!r}"
