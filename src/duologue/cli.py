import typer
import uvicorn

from . import client as chat_client
from .server import app

cli = typer.Typer()


@cli.command()
def server(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


@cli.command()
def client(name: str, chat_id: str | None = None):
    if not chat_id:
        chat_id = chat_client.create_chat()
        print(f"Created chat: {chat_id}")

    while True:
        user_message = input(">>> ")
        updated_message = chat_client.send_message(chat_id, name, user_message)
        print(updated_message)
