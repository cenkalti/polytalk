import requests
import typer
import uvicorn

from .chat import PROMPT
from .server import app

cli = typer.Typer()


@cli.command()
def server(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


@cli.command()
def client(name: str, chat_id: str | None = None):
    BASE_URL = "http://localhost:8000"

    if not chat_id:
        response = requests.post(f"{BASE_URL}/chat", json={"prompt": PROMPT})
        response.raise_for_status()
        chat_id = response.json()["id"]
        print(f"Created chat: {chat_id}")

    while True:
        user_message = input(">>> ")
        response = requests.post(
            f"{BASE_URL}/chat/{chat_id}/message",
            json={"name": name, "message": user_message},
        )
        response.raise_for_status()
        updated_message = response.json()["message"]
        print(updated_message)
