import pytest

import config


def test_get_env_api_key_returns_none_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(config.ENV_API_KEY_VAR, raising=False)
    assert config.get_env_api_key() is None


def test_get_env_api_key_returns_none_for_blank_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(config.ENV_API_KEY_VAR, '')
    assert config.get_env_api_key() is None


def test_get_env_api_key_returns_value_when_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(config.ENV_API_KEY_VAR, 'server-key')
    assert config.get_env_api_key() == 'server-key'


def test_default_model_is_in_available_models() -> None:
    assert config.DEFAULT_MODEL in config.AVAILABLE_MODELS
