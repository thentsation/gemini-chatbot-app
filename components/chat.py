import streamlit as st
from services.response import get_answer
from utils.streaming import response_generator
from components.feedback import feedback_system
from utils.state_manager import add_message

def chat_interface(model):
    if prompt := st.chat_input("Type your message:", key="user_message"):
        with st.chat_message("user"):
            st.markdown(prompt)
        add_message("user", prompt)

        try:
            response = get_answer(model, prompt)
        except RuntimeError as e:
            st.error(str(e))
            return

        with st.chat_message("assistant", avatar="🤖"):
            response_text = st.write_stream(response_generator(response))
        add_message("assistant", response_text)

        feedback_system(response)
