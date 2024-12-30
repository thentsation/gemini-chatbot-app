import streamlit as st

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def reset_chat():
    st.session_state.messages = []
    st.success("Chat cleared successfully!")
