"""End-to-end smoke test for the whole app via Streamlit's AppTest, with the
google-genai SDK faked out so no real network call is made."""

from collections.abc import Iterator
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeChat:
    def __init__(self, *, fail: bool = False) -> None:
        self.sent: list[str] = []
        self.fail = fail

    def send_message(self, prompt: str) -> _FakeResponse:
        if self.fail:
            raise RuntimeError(
                'Cota da API excedida. Aguarde um pouco ou utilize outra chave.'
            )
        self.sent.append(prompt)
        return _FakeResponse(f'echo: {prompt}')


class _FakeModels:
    def list(self, config: Any = None) -> Iterator[object]:
        return iter([object()])


class _FakeChats:
    def __init__(self, *, fail: bool) -> None:
        self.fail = fail

    def create(self, model: str) -> _FakeChat:
        return _FakeChat(fail=self.fail)


class _FakeClient:
    def __init__(self, api_key: str | None = None, *, fail: bool = False) -> None:
        self.api_key = api_key
        self.models = _FakeModels()
        self.chats = _FakeChats(fail=fail)


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    monkeypatch.setattr('google.genai.Client', _FakeClient)
    at = AppTest.from_file('../src/app.py')
    at.run()
    return at


@pytest.fixture
def app_with_failing_model(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    monkeypatch.setattr(
        'google.genai.Client', lambda api_key=None: _FakeClient(api_key, fail=True)
    )
    at = AppTest.from_file('../src/app.py')
    at.run()
    return at


def test_prompts_for_api_key_when_missing(app: AppTest) -> None:
    assert not app.exception
    assert any('API Key' in info.value for info in app.info)


def test_sends_message_and_keeps_history_across_reruns(app: AppTest) -> None:
    app.sidebar.text_input[0].set_value('fake-key').run()
    app.chat_input[0].set_value('Olá, tudo bem?').run()

    assert not app.exception
    contents = [msg.markdown[0].value for msg in app.chat_message]
    assert 'Olá, tudo bem?' in contents
    assert 'echo: Olá, tudo bem?' in contents

    # A second turn must not wipe out the first — this is the history bug fix.
    app.chat_input[0].set_value('E agora?').run()
    contents = [msg.markdown[0].value for msg in app.chat_message]
    assert 'Olá, tudo bem?' in contents
    assert 'E agora?' in contents
    assert 'echo: E agora?' in contents


def test_clear_chat_resets_history(app: AppTest) -> None:
    app.sidebar.text_input[0].set_value('fake-key').run()
    app.chat_input[0].set_value('mensagem').run()
    assert len(app.chat_message) > 0

    app.sidebar.button[0].click().run()
    assert len(app.chat_message) == 0


def test_feedback_is_submitted_and_persists_across_reruns(app: AppTest) -> None:
    app.sidebar.text_input[0].set_value('fake-key').run()
    app.chat_input[0].set_value('primeira mensagem').run()

    app.radio[0].set_value('Parcialmente útil').run()
    app.button[0].click().run()

    captions = [c.value for c in app.caption]
    assert any('Parcialmente útil' in value for value in captions)

    # A second turn re-renders the whole history; the earlier rating must stick.
    app.chat_input[0].set_value('segunda mensagem').run()
    captions = [c.value for c in app.caption]
    assert any('Parcialmente útil' in value for value in captions)


def test_generation_error_is_shown_without_corrupting_history(
    app_with_failing_model: AppTest,
) -> None:
    at = app_with_failing_model
    at.sidebar.text_input[0].set_value('fake-key').run()
    at.chat_input[0].set_value('mensagem').run()

    assert not at.exception
    assert any('Cota da API excedida' in err.value for err in at.error)
    contents = [msg.markdown[0].value for msg in at.chat_message if msg.markdown]
    assert contents == ['mensagem']


def test_server_provisioned_api_key_skips_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr('google.genai.Client', _FakeClient)
    monkeypatch.setenv('GOOGLE_API_KEY', 'server-key')

    at = AppTest.from_file('../src/app.py')
    at.run()

    assert not at.exception
    assert len(at.sidebar.text_input) == 0
    assert any(
        'chave de API configurada no servidor' in s.value for s in at.sidebar.success
    )
