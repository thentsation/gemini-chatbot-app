from collections.abc import Iterator
from typing import Any

import pytest
import streamlit as st
from google.genai import errors

from services import google_api


class _FakeChat:
    pass


class _FakeChats:
    def create(self, model: str) -> _FakeChat:
        return _FakeChat()


class _FakeModels:
    def __init__(self, fail: bool) -> None:
        self._fail = fail

    def list(self, config: Any = None) -> Iterator[object]:
        if self._fail:
            raise errors.APIError(403, {'error': {'message': 'invalid key'}})
        return iter([object()])


class _FakeClient:
    def __init__(self, api_key: str | None = None, fail: bool = False) -> None:
        self.api_key = api_key
        self.models = _FakeModels(fail)
        self.chats = _FakeChats()


def setup_function() -> None:
    st.session_state.clear()


@pytest.mark.parametrize(
    ('code', 'expected'),
    [
        (401, 'inválida'),
        (403, 'inválida'),
        (404, 'indisponível'),
        (429, 'Cota da API excedida'),
        (500, 'Erro ao comunicar'),
    ],
)
def test_describe_api_error_maps_known_codes(code: int, expected: str) -> None:
    exc = errors.APIError(code, {'error': {'message': 'boom'}})
    assert expected in google_api.describe_api_error(exc)


def test_get_chat_session_returns_session_for_valid_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        google_api.genai, 'Client', lambda api_key: _FakeClient(api_key)
    )
    session = google_api.get_chat_session('good-key', 'gemini-3.8-flash')
    assert isinstance(session, _FakeChat)
    assert st.session_state['_chat_cache_key'] == ('good-key', 'gemini-3.8-flash')


def test_get_chat_session_reuses_cached_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = []

    def fake_client(api_key: str) -> _FakeClient:
        created.append(api_key)
        return _FakeClient(api_key)

    monkeypatch.setattr(google_api.genai, 'Client', fake_client)
    first = google_api.get_chat_session('good-key', 'gemini-3.8-flash')
    second = google_api.get_chat_session('good-key', 'gemini-3.8-flash')

    assert first is second
    assert created == ['good-key']


def test_get_chat_session_returns_none_for_invalid_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        google_api.genai, 'Client', lambda api_key: _FakeClient(api_key, fail=True)
    )
    monkeypatch.setattr(st, 'error', lambda *_args, **_kwargs: None)

    session = google_api.get_chat_session('bad-key', 'gemini-3.8-flash')

    assert session is None
    assert '_chat_cache_key' not in st.session_state
