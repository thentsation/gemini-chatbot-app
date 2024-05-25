# app.py
from typing import List, Union
import os

from dotenv import load_dotenv, find_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import streamlit as st


# Configura a página principal da aplicação.
def init_page() -> None:
    st.set_page_config(
        page_title="Personal ChatGPT"
    )
    st.header("Personal ChatGPT")
    st.sidebar.title("Options")


# Inicializa e gerencia as mensagens da sessão do usuário.
def init_messages() -> None:
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(
                content="You are a helpful AI assistant. Reply your answer in markdown format.")
        ]
        st.session_state.costs = []


# Seleciona o modelo de linguagem a ser utilizado.
def select_llm() -> ChatOpenAI:
    model_name = st.sidebar.radio("Choose LLM:",
                                  ("gpt-3.5-turbo-0613", "gpt-4"))
    temperature = st.sidebar.slider("Temperature:", min_value=0.0,
                                    max_value=1.0, value=0.0, step=0.01)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(temperature=temperature, model_name=model_name, openai_api_key=openai_api_key)


# Obtém a resposta do modelo de linguagem e o custo total da chamada.
def get_answer(llm, messages) -> tuple[str, float]:
    with get_openai_callback() as cb:
        answer = llm(messages)
    return answer.content, cb.total_cost


# Função principal da aplicação.
def main() -> None:
    _ = load_dotenv(find_dotenv())

    init_page()
    llm = select_llm()
    init_messages()


    if user_input := st.chat_input("Input your question!"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            answer, cost = get_answer(llm, st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=answer))
        st.session_state.costs.append(cost)


    messages = st.session_state.get("messages", [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    costs = st.session_state.get("costs", [])
    st.sidebar.markdown("## Costs")
    st.sidebar.markdown(f"**Total cost: ${sum(costs):.5f}**")
    for cost in costs:
        st.sidebar.markdown(f"- ${cost:.5f}")

if __name__ == "__main__":
    main()
