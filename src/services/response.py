"""Sends a prompt to an active chat session and returns the model's reply."""

from google.genai import errors
from google.genai.chats import Chat

from services.google_api import describe_api_error


def get_answer(chat_session: Chat, prompt: str) -> str:
    try:
        response = chat_session.send_message(prompt)
    except errors.APIError as exc:
        raise RuntimeError(describe_api_error(exc)) from exc

    if not response.text:
        raise RuntimeError(
            'O modelo não retornou uma resposta em texto para esta mensagem.'
        )
    return response.text
