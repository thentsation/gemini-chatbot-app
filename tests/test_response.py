import pytest
from google.genai import errors

from services.response import get_answer


class _FakeResponse:
    def __init__(self, text: str | None) -> None:
        self.text = text


class _FakeChat:
    def __init__(self, result: object) -> None:
        self._result = result

    def send_message(self, prompt: str) -> _FakeResponse:
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def test_get_answer_returns_response_text() -> None:
    chat = _FakeChat(_FakeResponse('olá!'))
    assert get_answer(chat, 'oi') == 'olá!'


def test_get_answer_raises_runtime_error_on_empty_text() -> None:
    chat = _FakeChat(_FakeResponse(''))
    with pytest.raises(RuntimeError, match='não retornou uma resposta'):
        get_answer(chat, 'oi')


def test_get_answer_translates_api_error() -> None:
    api_error = errors.APIError(429, {'error': {'message': 'quota'}})
    chat = _FakeChat(api_error)
    with pytest.raises(RuntimeError, match='Cota da API excedida'):
        get_answer(chat, 'oi')
