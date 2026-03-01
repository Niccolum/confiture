from dature.fields.secret_str import SecretStr


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
