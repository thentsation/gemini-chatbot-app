import streamlit as st
import textwrap

import google.generativeai as genai

from IPython.display import Markdown


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# Configurando a chave da API
google_api_key = st.text_input("Digite sua chave da API do Google:")

if not google_api_key:
    st.warning("Por favor, insira sua chave da API do Google.")
else:
    # Configurando a chave da API
    genai.configure(api_key=google_api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')

    st.sidebar.title("Options")


    # Obtém a resposta do modelo de linguagem
    def get_answer(prompt):
        response = model.generate_content(prompt)
        return response.text


    # Função principal da aplicação.
    def main():
        user_input = st.text_input("Você:", key="user_input")

        if st.button("Enviar"):
            response = get_answer(user_input)
            st.write("ChatGPT:", response)


    if __name__ == "__main__":
        main()
