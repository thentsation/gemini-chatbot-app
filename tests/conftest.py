import streamlit as st


def pytest_runtest_setup() -> None:
    st.session_state.clear()
