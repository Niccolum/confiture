import math
from dataclasses import fields

from examples.all_types_dataclass import AllPythonTypesCompact


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
