import streamlit as st
import google.generativeai as genai
import time

# Função para obter a resposta do modelo
def get_answer(prompt):
    response = model.generate_content(prompt)
    return response.text

# Função para adicionar uma mensagem à sessão
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Função para configurar a API do Google e carregar o modelo
def setup_google_api():
    with st.sidebar:
        st.write("### Configurações")
        google_api_key = st.text_input("Digite sua chave da API do Google:", type="password")

        if not google_api_key:
            st.warning("Por favor, insira sua chave da API do Google.")
            return None
        else:
            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


# Função principal
def main():
    if prompt := st.chat_input("Digite sua mensagem:", key="user_message"):
        with st.chat_message("user"):
            st.markdown(prompt)
        add_message("user", prompt)

        response = get_answer(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(response))
        add_message("ChatGPT", response)

st.title("ChatGemini")

# Verificar se a sessão de mensagens existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configurar a API do Google e carregar o modelo
model = setup_google_api()

# Executar a função principal se o modelo foi configurado com sucesso
if model:
    main()
