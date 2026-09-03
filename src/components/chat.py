"""Renders chat history and handles new messages against an active chat session."""

import streamlit as st
from google.genai.chats import Chat

from components.feedback import feedback_system
from services.response import get_answer
from utils.state_manager import add_message
from utils.streaming import response_generator


def chat_interface(chat_session: Chat) -> None:
    for index, message in enumerate(st.session_state.messages):
        avatar = '🤖' if message['role'] == 'assistant' else None
        with st.chat_message(message['role'], avatar=avatar):
            st.markdown(message['content'])
            if message['role'] == 'assistant':
                feedback_system(index)

    prompt = st.chat_input('Digite sua mensagem...')
    if not prompt:
        return

    with st.chat_message('user'):
        st.markdown(prompt)
    add_message('user', prompt)

    with st.chat_message('assistant', avatar='🤖'):
        with st.spinner('Pensando...'):
            try:
                response_text = get_answer(chat_session, prompt)
            except RuntimeError as exc:
                st.error(str(exc))
                return
        st.write_stream(response_generator(response_text))

    add_message('assistant', response_text)
    st.rerun()
