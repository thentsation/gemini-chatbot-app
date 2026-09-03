"""Owns everything kept in st.session_state for the chat UI."""

import streamlit as st


def initialize_session_state() -> None:
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'feedback_log' not in st.session_state:
        st.session_state.feedback_log = {}


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({'role': role, 'content': content})


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.feedback_log = {}
    st.session_state.pop('chat_session', None)
    st.session_state.pop('_chat_cache_key', None)
    st.toast('Conversa reiniciada.')
