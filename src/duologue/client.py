import requests

from .chat import PROMPT

BASE_URL = "http://localhost:8000"


def create_chat() -> str:
    url = f"{BASE_URL}/chat"
    data = {"prompt": PROMPT}
    response = requests.post(url, json=data)
    response.raise_for_status()
    chat_id = response.json()["id"]
    return chat_id


def send_message(chat_id: str, name: str, message: str) -> str:
    url = f"{BASE_URL}/chat/{chat_id}/message"
    data = {"name": name, "message": message}
    response = requests.post(url, json=data)
    response.raise_for_status()
    updated_message = response.json()["message"]
    return updated_message
