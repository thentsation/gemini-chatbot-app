"""Sidebar: API key (BYOK or server-provisioned), model picker, clear-chat action."""

import streamlit as st

from config import AVAILABLE_MODELS, DEFAULT_MODEL, get_env_api_key
from utils.state_manager import reset_chat


def setup_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.header('⚙️ Configurações')

        env_api_key = get_env_api_key()
        if env_api_key:
            st.success('Usando a chave de API configurada no servidor.')
            api_key = env_api_key
        else:
            api_key = st.text_input(
                'Google API Key',
                type='password',
                help='Gere sua chave gratuita em https://aistudio.google.com/apikey',
            )
            st.caption(
                'Sua chave não é armazenada em disco nem registrada em logs — '
                'fica apenas na memória desta sessão do navegador.'
            )

        model = st.selectbox(
            'Modelo',
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(DEFAULT_MODEL),
            help="Modelos 'flash' são mais rápidos e baratos; 'pro' prioriza qualidade da resposta.",
        )

        st.divider()
        st.button('🗑️ Limpar conversa', on_click=reset_chat, use_container_width=True)

        return api_key, model
