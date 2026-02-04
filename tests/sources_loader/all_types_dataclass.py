"""Comprehensive dataclass with all Python basic types without repetition."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo


@dataclass
class AllPythonTypesCompact:
    """
    Comprehensive dataclass containing all Python basic types.
    Each field demonstrates a unique type or pattern.
    """

    string_value: str
    integer_value: int
    float_value: float
    boolean_value: bool
    none_value: None

    list_strings: list[str]
    list_integers: list[int]
    list_mixed: list[Any]
    list_nested: list[list[str]]
    list_dicts: list[dict[str, Any]]

    tuple_simple: tuple[int, int, int]
    tuple_mixed: tuple[str, int, bool]
    tuple_nested: tuple[tuple[int, ...], tuple[str, ...]]

    set_integers: set[int]
    set_strings: set[str]

    dict_simple: dict[str, str]
    dict_mixed: dict[str, Any]
    dict_nested: dict[str, dict[str, Any]]
    dict_int_keys: dict[int, str]

    date_value: date
    datetime_value: datetime
    datetime_value_with_timezone: datetime
    datetime_value_with_z_timezone: datetime
    time_value: time
    bytes_value: bytes
    bytearray_value: bytearray
    complex_value: complex

    empty_string: str
    empty_list: list[Any]
    empty_dict: dict[str, Any]
    zero_int: int
    zero_float: float
    false_bool: bool

    optional_string: str | None
    union_type: int | float | str
    nested_optional: list[dict[str, str | None]]

    range_values: list[int]

    frozenset_value: frozenset[int] | None = None


EXPECTED_ALL_TYPES = AllPythonTypesCompact(
    string_value="hello world",
    integer_value=42,
    float_value=3.14159,
    boolean_value=True,
    none_value=None,
    list_strings=["item1", "item2", "item3"],
    list_integers=[1, 2, 3, 4, 5],
    list_mixed=["string", 42, 3.14, True, None],
    list_nested=[["a", "b"], ["c", "d"]],
    list_dicts=[
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ],
    tuple_simple=(1, 2, 3),
    tuple_mixed=("text", 42, True),
    tuple_nested=((1, 2, 3), ("a", "b", "c")),
    set_integers={1, 2, 3, 4, 5},
    set_strings={"apple", "banana", "cherry"},
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
    date_value=date(2024, 1, 15),
    datetime_value=datetime(2024, 1, 15, 10, 30),
    datetime_value_with_timezone=datetime(2024, 1, 15, 10, 30, tzinfo=ZoneInfo("Europe/Moscow")),
    datetime_value_with_z_timezone=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
    time_value=time(10, 30),
    bytes_value=b"binary data",
    bytearray_value=bytearray(b"binary"),
    complex_value=1 + 2j,
    empty_string="",
    empty_list=[],
    empty_dict={},
    zero_int=0,
    zero_float=0.0,
    false_bool=False,
    optional_string=None,
    union_type=42,
    nested_optional=[
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": None},
    ],
    range_values=[0, 2, 4, 6, 8],
    frozenset_value=frozenset({1, 2, 3, 4, 5}),
)
