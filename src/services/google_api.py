"""Wraps the google-genai SDK: client/chat-session lifecycle and error mapping."""

import streamlit as st
from google import genai
from google.genai import errors
from google.genai.chats import Chat


class InvalidAPIKeyError(RuntimeError):
    """Raised when the provided API key is rejected by the Gemini API."""


def describe_api_error(exc: errors.APIError) -> str:
    """Translate a raw APIError into a message a chat user can act on."""
    if exc.code in (400, 401, 403):
        return 'Chave de API inválida ou sem permissão para este modelo. Verifique a chave e tente novamente.'
    if exc.code == 404:
        return 'Modelo indisponível no momento. Tente selecionar outro modelo na barra lateral.'
    if exc.code == 429:
        return 'Cota da API excedida. Aguarde um pouco ou utilize outra chave.'
    return f'Erro ao comunicar com a API do Gemini: {exc.message}'


def _validate_api_key(client: genai.Client) -> None:
    try:
        next(iter(client.models.list(config={'page_size': 1})))
    except errors.APIError as exc:
        raise InvalidAPIKeyError(describe_api_error(exc)) from exc


def get_chat_session(api_key: str, model: str) -> Chat | None:
    """Return a cached chat session for this (api_key, model) pair.

    A new google-genai Chat keeps its own turn history internally, which is
    what gives the assistant real conversational memory. Recreated whenever
    the key or model changes so the switch takes effect immediately.
    """
    cache_key = (api_key, model)
    if st.session_state.get('_chat_cache_key') == cache_key:
        return st.session_state.get('chat_session')

    client = genai.Client(api_key=api_key)
    try:
        _validate_api_key(client)
    except InvalidAPIKeyError as exc:
        st.session_state.pop('chat_session', None)
        st.session_state.pop('_chat_cache_key', None)
        st.error(str(exc))
        return None

    st.session_state.chat_session = client.chats.create(model=model)
    st.session_state._chat_cache_key = cache_key
    return st.session_state.chat_session
