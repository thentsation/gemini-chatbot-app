"""Central configuration for the Gemini Chatbot App."""

import os

import streamlit as st

APP_TITLE = 'Gemini Chatbot'
APP_ICON = '🤖'

AVAILABLE_MODELS = [
    'gemini-3.8-flash',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-3.1-pro-preview',
]
DEFAULT_MODEL = AVAILABLE_MODELS[0]

ENV_API_KEY_VAR = 'GOOGLE_API_KEY'


def get_env_api_key() -> str | None:
    """Return the server-provisioned API key, if any."""
    return os.environ.get(ENV_API_KEY_VAR) or None


def configure_page() -> None:
    """Set the browser tab title/icon. Must run before any other st.* call."""
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout='centered')
