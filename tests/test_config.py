import pytest

from dature.config import (
    ErrorDisplayConfig,
    LoadingConfig,
    MaskingConfig,
    _ConfigProxy,
    config,
    configure,
)
from dature.errors import DatureConfigError


@pytest.mark.usefixtures("_reset_config")
class TestConfigProxy:
    @staticmethod
    def test_proxy_caches_instance() -> None:
        first = config.ensure_loaded()
        second = config.ensure_loaded()
        assert first is second


@pytest.mark.usefixtures("_reset_config")
class TestConfigure:
    @staticmethod
    @pytest.mark.parametrize(
        ("kwargs", "attr_path", "expected"),
        [
            (
                {"masking": MaskingConfig(mask_char="X", fixed_mask_length=10)},
                ("masking", "mask_char"),
                "X",
            ),
            (
                {"masking": MaskingConfig(mask_char="X", fixed_mask_length=10)},
                ("masking", "fixed_mask_length"),
                10,
            ),
            (
                {"error_display": ErrorDisplayConfig(max_visible_lines=10)},
                ("error_display", "max_visible_lines"),
                10,
            ),
            (
                {"loading": LoadingConfig(cache=False, debug=True)},
                ("loading", "cache"),
                False,
            ),
            (
                {"loading": LoadingConfig(cache=False, debug=True)},
                ("loading", "debug"),
                True,
            ),
        ],
        ids=[
            "masking-mask_char",
            "masking-fixed_mask_length",
            "error_display-max_visible_lines",
            "loading-cache",
            "loading-debug",
        ],
    )
    def test_configure_overrides(
        kwargs: dict[str, MaskingConfig | ErrorDisplayConfig | LoadingConfig],
        attr_path: tuple[str, str],
        expected: str | int | bool,
    ) -> None:
        configure(**kwargs)
        group = getattr(config, attr_path[0])
        assert getattr(group, attr_path[1]) == expected

    @staticmethod
    @pytest.mark.parametrize(
        ("kwargs", "unchanged_group", "expected_default"),
        [
            (
                {"masking": MaskingConfig(mask_char="#")},
                "error_display",
                ErrorDisplayConfig(),
            ),
            (
                {"masking": MaskingConfig(mask_char="#")},
                "loading",
                LoadingConfig(),
            ),
            (
                {"error_display": ErrorDisplayConfig(max_visible_lines=10)},
                "masking",
                MaskingConfig(),
            ),
        ],
        ids=[
            "masking-preserves-error_display",
            "masking-preserves-loading",
            "error_display-preserves-masking",
        ],
    )
    def test_configure_preserves_other_groups(
        kwargs: dict[str, MaskingConfig | ErrorDisplayConfig | LoadingConfig],
        unchanged_group: str,
        expected_default: MaskingConfig | ErrorDisplayConfig | LoadingConfig,
    ) -> None:
        configure(**kwargs)
        assert getattr(config, unchanged_group) == expected_default


@pytest.mark.usefixtures("_reset_config")
class TestEnvLoading:
    @staticmethod
    @pytest.mark.parametrize(
        ("env_var", "env_value", "attr_path", "expected"),
        [
            (
                "DATURE_MASKING__MASK_CHAR",
                "X",
                ("masking", "mask_char"),
                "X",
            ),
            (
                "DATURE_MASKING__MIN_VISIBLE_CHARS",
                "4",
                ("masking", "min_visible_chars"),
                4,
            ),
            (
                "DATURE_LOADING__CACHE",
                "false",
                ("loading", "cache"),
                False,
            ),
            (
                "DATURE_LOADING__DEBUG",
                "true",
                ("loading", "debug"),
                True,
            ),
            (
                "DATURE_MASKING__MASK_SECRETS",
                "false",
                ("masking", "mask_secrets"),
                False,
            ),
            (
                "DATURE_MASKING__SECRET_FIELD_NAMES",
                '["password","token","secret"]',
                ("masking", "secret_field_names"),
                ("password", "token", "secret"),
            ),
        ],
        ids=[
            "str-mask_char",
            "int-min_visible_chars",
            "bool-cache-false",
            "bool-debug-true",
            "bool-mask_secrets-false",
            "tuple-secret_field_names",
        ],
    )
    def test_env_loading(
        monkeypatch: pytest.MonkeyPatch,
        env_var: str,
        env_value: str,
        attr_path: tuple[str, str],
        expected: str | int | bool | tuple[str, ...],
    ) -> None:
        monkeypatch.setenv(env_var, env_value)
        _ConfigProxy.set_instance(None)
        group = getattr(config, attr_path[0])
        assert getattr(group, attr_path[1]) == expected


@pytest.mark.usefixtures("_reset_config")
class TestValidation:
    @staticmethod
    @pytest.mark.parametrize(
        ("env_var", "env_value", "attr"),
        [
            ("DATURE_MASKING__MASK_CHAR", "", "masking"),
            ("DATURE_MASKING__MIN_VISIBLE_CHARS", "0", "masking"),
            ("DATURE_ERROR_DISPLAY__MAX_VISIBLE_LINES", "0", "error_display"),
        ],
        ids=[
            "empty-mask_char",
            "zero-min_visible_chars",
            "zero-max_visible_lines",
        ],
    )
    def test_invalid_env_raises(
        monkeypatch: pytest.MonkeyPatch,
        env_var: str,
        env_value: str,
        attr: str,
    ) -> None:
        monkeypatch.setenv(env_var, env_value)
        _ConfigProxy.set_instance(None)
        with pytest.raises(DatureConfigError):
            _ = getattr(config, attr)
