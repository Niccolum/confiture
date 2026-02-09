"""Tests for custom fields: SecretStr, PaymentCardNumber, ByteSize."""

import operator
from collections.abc import Callable

import pytest

from dature.fields import ByteSize, PaymentCardNumber, SecretStr


class TestSecretStr:
    def test_get_secret_value(self) -> None:
        secret = SecretStr("my_secret")
        assert secret.get_secret_value() == "my_secret"

    def test_str_masks_value(self) -> None:
        secret = SecretStr("my_secret")
        assert str(secret) == "**********"

    def test_repr_masks_value(self) -> None:
        secret = SecretStr("my_secret")
        assert repr(secret) == "SecretStr('**********')"

    def test_eq(self) -> None:
        assert SecretStr("abc") == SecretStr("abc")
        assert SecretStr("abc") != SecretStr("xyz")

    def test_eq_different_type(self) -> None:
        assert SecretStr("abc") != "abc"

    def test_hash(self) -> None:
        assert hash(SecretStr("abc")) == hash(SecretStr("abc"))
        assert hash(SecretStr("abc")) != hash(SecretStr("xyz"))

    def test_len(self) -> None:
        assert len(SecretStr("hello")) == 5
        assert len(SecretStr("")) == 0


class TestPaymentCardNumber:
    @pytest.mark.parametrize(
        ("card_number", "expected_brand", "expected_masked"),
        [
            ("4111111111111111", "Visa", "************1111"),
            ("5500000000000004", "Mastercard", "************0004"),
            ("378282246310005", "American Express", "***********0005"),
            ("2200000000000004", "Mir", "************0004"),
            ("3530111333300000", "JCB", "************0000"),
            ("4111 1111 1111 1111", "Visa", "************1111"),
            ("4111-1111-1111-1111", "Visa", "************1111"),
        ],
    )
    def test_brand_and_masked(
        self,
        card_number: str,
        expected_brand: str,
        expected_masked: str,
    ) -> None:
        card = PaymentCardNumber(card_number)
        assert card.brand == expected_brand
        assert card.masked == expected_masked

    def test_str_returns_masked(self) -> None:
        card = PaymentCardNumber("4111111111111111")
        assert str(card) == "************1111"

    def test_repr(self) -> None:
        card = PaymentCardNumber("4111111111111111")
        assert repr(card) == "PaymentCardNumber('************1111')"

    def test_eq(self) -> None:
        assert PaymentCardNumber("4111111111111111") == PaymentCardNumber("4111111111111111")
        assert PaymentCardNumber("4111111111111111") != PaymentCardNumber("5500000000000004")

    def test_hash(self) -> None:
        assert hash(PaymentCardNumber("4111111111111111")) == hash(PaymentCardNumber("4111111111111111"))

    @pytest.mark.parametrize(
        ("card_number", "error_match"),
        [
            ("4111111111111112", "Luhn"),
            ("41111111abcd1111", "digits"),
            ("411111", "12-19 digits"),
            ("41111111111111111111", "12-19 digits"),
        ],
    )
    def test_invalid(self, card_number: str, error_match: str) -> None:
        with pytest.raises(ValueError, match=error_match):
            PaymentCardNumber(card_number)


class TestByteSize:
    @pytest.mark.parametrize(
        ("input_value", "expected_bytes"),
        [
            ("1.5 GB", 1_500_000_000),
            ("1 KiB", 1024),
            ("1024", 1024),
            ("0 B", 0),
            ("500 MB", 500_000_000),
            ("2.5 GiB", int(2.5 * 2**30)),
            ("1 TB", 1_000_000_000_000),
        ],
    )
    def test_parse(self, input_value: str, expected_bytes: int) -> None:
        assert int(ByteSize(input_value)) == expected_bytes

    def test_from_int(self) -> None:
        bs = ByteSize(1024)
        assert int(bs) == 1024

    @pytest.mark.parametrize(
        ("value", "decimal", "expected"),
        [
            (1024, False, "1KiB"),
            (2**20, False, "1MiB"),
            (2**30, False, "1GiB"),
            (0, False, "0B"),
            (1000, True, "1KB"),
            (1_000_000, True, "1MB"),
            (1_500_000_000, True, "1.5GB"),
        ],
    )
    def test_human_readable(self, value: int, decimal: bool, expected: str) -> None:
        assert ByteSize(value).human_readable(decimal=decimal) == expected

    def test_str(self) -> None:
        assert str(ByteSize(1024)) == "1KiB"

    def test_repr(self) -> None:
        assert repr(ByteSize(1024)) == "ByteSize(1024)"

    def test_eq(self) -> None:
        assert ByteSize(1024) == ByteSize(1024)
        assert ByteSize(1024) != ByteSize(2048)

    def test_hash(self) -> None:
        assert hash(ByteSize(1024)) == hash(ByteSize(1024))

    @pytest.mark.parametrize(
        ("left", "right", "op"),
        [
            (100, 200, operator.lt),
            (200, 100, operator.gt),
            (100, 200, operator.le),
            (100, 100, operator.le),
            (200, 100, operator.ge),
            (100, 100, operator.ge),
        ],
    )
    def test_comparison_true(
        self,
        left: int,
        right: int,
        op: Callable[[ByteSize, ByteSize], bool],
    ) -> None:
        assert op(ByteSize(left), ByteSize(right))

    @pytest.mark.parametrize(
        ("left", "right", "op"),
        [
            (200, 100, operator.lt),
            (100, 200, operator.gt),
        ],
    )
    def test_comparison_false(
        self,
        left: int,
        right: int,
        op: Callable[[ByteSize, ByteSize], bool],
    ) -> None:
        assert not op(ByteSize(left), ByteSize(right))

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            ("not a size", "Invalid byte size"),
            ("100 XB", "Unknown unit"),
        ],
    )
    def test_invalid(self, value: str, error_match: str) -> None:
        with pytest.raises(ValueError, match=error_match):
            ByteSize(value)
