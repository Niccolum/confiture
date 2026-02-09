import re
from typing import ClassVar


class SecretStr:
    __slots__ = ("_secret_value",)

    def __init__(self, secret_value: str) -> None:
        self._secret_value = secret_value

    def get_secret_value(self) -> str:
        return self._secret_value

    def __str__(self) -> str:
        return "**********"

    def __repr__(self) -> str:
        return "SecretStr('**********')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretStr):
            return NotImplemented
        return self._secret_value == other._secret_value

    def __hash__(self) -> int:
        return hash(self._secret_value)

    def __len__(self) -> int:
        return len(self._secret_value)


class PaymentCardNumber:
    __slots__ = ("_number",)

    _MIN_LENGTH: ClassVar[int] = 12
    _MAX_LENGTH: ClassVar[int] = 19
    _LUHN_DOUBLE_THRESHOLD: ClassVar[int] = 9

    _BRAND_RULES: ClassVar[list[tuple[str, int, int, int]]] = [
        # 6 digits
        ("Verve", 6, 506099, 506198),
        ("Verve", 6, 650002, 650027),
        ("Discover", 6, 622126, 622925),
        # 4 digits
        ("Mir", 4, 2200, 2204),
        ("JCB", 4, 3528, 3589),
        ("Mastercard", 4, 2221, 2720),
        ("Discover", 4, 6011, 6011),
        ("Maestro", 4, 5018, 5018),
        ("Maestro", 4, 5020, 5020),
        ("Maestro", 4, 5038, 5038),
        ("Maestro", 4, 5893, 5893),
        ("Maestro", 4, 6304, 6304),
        ("Maestro", 4, 6759, 6759),
        ("Maestro", 4, 6761, 6763),
        ("Troy", 4, 9792, 9792),
        # 3 digits
        ("Diners Club", 3, 300, 305),
        ("Discover", 3, 644, 649),
        # 2 digits
        ("American Express", 2, 34, 34),
        ("American Express", 2, 37, 37),
        ("Mastercard", 2, 51, 55),
        ("RuPay", 2, 60, 60),
        ("UnionPay", 2, 62, 62),
        ("Discover", 2, 65, 65),
        ("Diners Club", 2, 36, 36),
        ("Diners Club", 2, 38, 38),
        ("Maestro", 2, 67, 67),
        # 1 digit
        ("Visa", 1, 4, 4),
    ]

    def __init__(self, card_number: str) -> None:
        cleaned = card_number.replace(" ", "").replace("-", "")

        if not cleaned.isdigit():
            msg = f"Card number must contain only digits, got: {card_number!r}"
            raise ValueError(msg)

        if not (self._MIN_LENGTH <= len(cleaned) <= self._MAX_LENGTH):
            msg = f"Card number must be {self._MIN_LENGTH}-{self._MAX_LENGTH} digits, got {len(cleaned)}"
            raise ValueError(msg)

        if not self._luhn_check(cleaned):
            msg = f"Card number failed Luhn check: {card_number!r}"
            raise ValueError(msg)

        self._number = cleaned

    @staticmethod
    def _luhn_check(number: str) -> bool:
        total = 0
        for i, digit_char in enumerate(reversed(number)):
            digit = int(digit_char)
            if i % 2 == 1:
                digit *= 2
                if digit > PaymentCardNumber._LUHN_DOUBLE_THRESHOLD:
                    digit -= PaymentCardNumber._LUHN_DOUBLE_THRESHOLD
            total += digit
        return total % 10 == 0

    @property
    def masked(self) -> str:
        return "*" * (len(self._number) - 4) + self._number[-4:]

    @property
    def brand(self) -> str:
        for brand_name, prefix_len, prefix_min, prefix_max in self._BRAND_RULES:
            if len(self._number) < prefix_len:
                continue
            prefix = int(self._number[:prefix_len])
            if prefix_min <= prefix <= prefix_max:
                return brand_name
        return "Unknown"

    def __str__(self) -> str:
        return self.masked

    def __repr__(self) -> str:
        return f"PaymentCardNumber('{self.masked}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PaymentCardNumber):
            return NotImplemented
        return self._number == other._number

    def __hash__(self) -> int:
        return hash(self._number)


class ByteSize:
    __slots__ = ("_bytes",)

    _UNITS: ClassVar[dict[str, int]] = {
        "b": 1,
        "kb": 10**3,
        "mb": 10**6,
        "gb": 10**9,
        "tb": 10**12,
        "pb": 10**15,
        "kib": 2**10,
        "mib": 2**20,
        "gib": 2**30,
        "tib": 2**40,
        "pib": 2**50,
    }

    _PARSE_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^\s*([0-9]*\.?[0-9]+)\s*([a-zA-Z]*)\s*$",
    )

    def __init__(self, value: int | str) -> None:
        if isinstance(value, int):
            self._bytes = value
        else:
            self._bytes = self._parse(value)

    @staticmethod
    def _parse(value: str) -> int:
        match = ByteSize._PARSE_RE.match(value)
        if match is None:
            msg = f"Invalid byte size format: {value!r}"
            raise ValueError(msg)

        number_str = match.group(1)
        unit_str = match.group(2).lower()

        if unit_str == "":
            unit_str = "b"

        if unit_str not in ByteSize._UNITS:
            msg = f"Unknown unit: {unit_str!r}"
            raise ValueError(msg)

        multiplier = ByteSize._UNITS[unit_str]
        return int(float(number_str) * multiplier)

    def human_readable(self, *, decimal: bool = False) -> str:
        if decimal:
            units = [("PB", 10**15), ("TB", 10**12), ("GB", 10**9), ("MB", 10**6), ("KB", 10**3)]
        else:
            units = [("PiB", 2**50), ("TiB", 2**40), ("GiB", 2**30), ("MiB", 2**20), ("KiB", 2**10)]

        for unit_name, threshold in units:
            if self._bytes >= threshold:
                size = self._bytes / threshold
                if size == int(size):
                    return f"{int(size)}{unit_name}"
                return f"{size:.1f}{unit_name}"

        return f"{self._bytes}B"

    def __int__(self) -> int:
        return self._bytes

    def __str__(self) -> str:
        return self.human_readable()

    def __repr__(self) -> str:
        return f"ByteSize({self._bytes})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ByteSize):
            return NotImplemented
        return self._bytes == other._bytes

    def __hash__(self) -> int:
        return hash(self._bytes)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ByteSize):
            return NotImplemented
        return self._bytes < other._bytes

    def __le__(self, other: object) -> bool:
        if not isinstance(other, ByteSize):
            return NotImplemented
        return self._bytes <= other._bytes

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, ByteSize):
            return NotImplemented
        return self._bytes > other._bytes

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, ByteSize):
            return NotImplemented
        return self._bytes >= other._bytes
