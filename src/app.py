import streamlit as st

from components.chat import chat_interface
from components.sidebar import setup_sidebar
from config import APP_ICON, APP_TITLE, configure_page
from services.google_api import get_chat_session
from utils.state_manager import initialize_session_state

configure_page()
st.title(f'{APP_ICON} {APP_TITLE}')
st.caption('Converse com o Gemini — sua chave, seu modelo, sua conversa.')

initialize_session_state()

api_key, model = setup_sidebar()

if not api_key:
    st.info('Adicione sua Google API Key na barra lateral para começar a conversar.')
else:
    chat_session = get_chat_session(api_key, model)
    if chat_session:
        chat_interface(chat_session)
