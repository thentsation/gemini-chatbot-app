import streamlit as st

from utils import state_manager


def setup_function() -> None:
    st.session_state.clear()


def test_initialize_session_state_sets_defaults() -> None:
    state_manager.initialize_session_state()
    assert st.session_state.messages == []
    assert st.session_state.feedback_log == {}


def test_initialize_session_state_is_idempotent() -> None:
    state_manager.initialize_session_state()
    state_manager.add_message('user', 'oi')
    state_manager.initialize_session_state()
    assert st.session_state.messages == [{'role': 'user', 'content': 'oi'}]


def test_add_message_appends_role_and_content() -> None:
    state_manager.initialize_session_state()
    state_manager.add_message('user', 'oi')
    state_manager.add_message('assistant', 'olá!')
    assert st.session_state.messages == [
        {'role': 'user', 'content': 'oi'},
        {'role': 'assistant', 'content': 'olá!'},
    ]


def test_reset_chat_clears_messages_feedback_and_session(monkeypatch) -> None:
    state_manager.initialize_session_state()
    state_manager.add_message('user', 'oi')
    st.session_state.feedback_log[0] = {'rating': 'Útil'}
    st.session_state.chat_session = object()
    st.session_state._chat_cache_key = ('key', 'model')

    monkeypatch.setattr(st, 'toast', lambda *_args, **_kwargs: None)
    state_manager.reset_chat()

    assert st.session_state.messages == []
    assert st.session_state.feedback_log == {}
    assert 'chat_session' not in st.session_state
    assert '_chat_cache_key' not in st.session_state
