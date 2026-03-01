from dataclasses import dataclass
from typing import Annotated

from dature.fields.payment_card import PaymentCardNumber
from dature.fields.secret_str import SecretStr
from dature.masking.detection import build_secret_paths


class TestBuildSecretPaths:
    def test_simple_secret_str(self):
        @dataclass
        class Cfg:
            api_key: SecretStr
            host: str

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"api_key"})

    def test_payment_card_number(self):
        @dataclass
        class Cfg:
            card: PaymentCardNumber
            name: str

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"card"})

    def test_name_based_detection(self):
        @dataclass
        class Cfg:
            password: str
            db_token: str
            host: str

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"password", "db_token"})

    def test_annotated_secret_str(self):
        @dataclass
        class Cfg:
            key: Annotated[SecretStr, "some metadata"]
            host: str

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"key"})

    def test_optional_secret_str(self):
        @dataclass
        class Cfg:
            key: SecretStr | None
            host: str

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"key"})

    def test_nested_dataclass(self):
        @dataclass
        class Inner:
            secret: SecretStr
            host: str

        @dataclass
        class Outer:
            inner: Inner
            name: str

        paths = build_secret_paths(Outer)
        assert paths == frozenset({"inner.secret"})

    def test_nested_name_based(self):
        @dataclass
        class DbConfig:
            password: str
            host: str

        @dataclass
        class Cfg:
            database: DbConfig

        paths = build_secret_paths(Cfg)
        assert paths == frozenset({"database.password"})

    def test_extra_patterns(self):
        @dataclass
        class Cfg:
            my_custom_field: str
            host: str

        paths = build_secret_paths(Cfg, extra_patterns=("custom",))
        assert paths == frozenset({"my_custom_field"})

    def test_caching(self):
        @dataclass
        class Cfg:
            password: str

        paths1 = build_secret_paths(Cfg)
        paths2 = build_secret_paths(Cfg)
        assert paths1 is paths2
