import streamlit as st
from utils.state_manager import reset_chat

def setup_sidebar():
    with st.sidebar:
        st.write("### Settings")
        google_api_key = st.text_input("Google API Key:", type="password")
        st.button('Clear Chat', on_click=reset_chat)
        return google_api_key
