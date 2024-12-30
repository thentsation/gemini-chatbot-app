import streamlit as st
from components.sidebar import setup_sidebar
from components.chat import chat_interface
from services.google_api import setup_google_api
from utils.state_manager import initialize_session_state

st.title("Gemini Chatbot App")

# Inicializar o estado da sessão
initialize_session_state()

# Configurar barra lateral e API do Google
google_api_key = setup_sidebar()
model = setup_google_api(google_api_key)

# Iniciar interface de chat se o modelo estiver configurado
if model:
    chat_interface(model)
