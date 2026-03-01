import pytest

from dature.fields.payment_card import PaymentCardNumber


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
