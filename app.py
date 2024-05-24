from typing import List, Union

from dotenv import load_dotenv, find_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import streamlit as st


def init_page() -> None:
    st.set_page_config(
        page_title="ChatGPT Personal"
    )
    st.header("ChatGPT Personal")
    st.sidebar.title("Options")


def init_messages() -> None:
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(
                content="You are a hepful AI assistant. Reply your answer in mardkown format.")
        ]
        st.session_state.costs = []


def select_llm() -> Union[ChatOpenAI, LlamaCpp]:
    model_name = st. sidebar.radio("Choose LLM:",
                                    ("gpt-3.5-turbo-0613", "gpt-4",
                                    "llama-2-7b-chat.ggmlv3.q2_k"))
    temperature = st.sidebar.slider("Temperature:", min_value=0.0,
                                    max_value=1.0, value=0.0, step=0.01)
    if model_name.startswith("gpt-"):
        return ChatOpenAI(temperature=temperature, model_name=model_name)
    elif model_name.startswith("llama-2-"):
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        return LlamaCpp(
            model_path=f"./models/{model_name}.bin",
            input={"temperature": temperature,
                   "max_length":2000,
                   "top_p": 1
                   },
            callback_manager=callback_manager
            verbose=False, # True
        )


def get_answer(llm, messages) -> tuple[str, float]:
    if isinstance(llm, ChatOpenAI):
        with get_openai_callback() as cb:
            answer = llm(messages)
        return answer.content, cb.total_cost
    if isinstance(llm, LlamaCpp):
        return llm(llama_v2_prompt(convert_langchainschema_to_dict(messages))), 0.0
        