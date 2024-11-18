import asyncio
import signal
from functools import wraps

import typer
import uvicorn
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from . import client as chat_client
from .server import app

cli = typer.Typer()


# https://github.com/fastapi/typer/issues/950
def cli_coro(signals=(signal.SIGHUP, signal.SIGTERM, signal.SIGINT), shutdown_func=None):
    """Decorator function that allows defining coroutines with click."""

    def decorator_cli_coro(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            if shutdown_func:
                for ss in signals:
                    loop.add_signal_handler(ss, shutdown_func, ss, loop)
            return loop.run_until_complete(f(*args, **kwargs))

        return wrapper

    return decorator_cli_coro


@cli.command()
def server(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


@cli.command()
@cli_coro()
async def client(name: str, chat_id: str | None = None):
    if not chat_id:
        chat_id = await chat_client.create_chat()
        print(f"Created chat with id: {chat_id}")

    session = PromptSession()

    async def read_user_input():
        while True:
            user_message = await session.prompt_async(">>> ")
            await chat_client.send_message(chat_id, name, user_message)

    async def print_incoming_messages():
        async for message in chat_client.connect_websocket(chat_id, name):
            print(message)

    with patch_stdout():
        await asyncio.gather(read_user_input(), print_incoming_messages())


@cli.command()
@cli_coro()
async def get_prompt(chat_id: str):
    print(await chat_client.get_prompt(chat_id))


@cli.command()
@cli_coro()
async def update_prompt(chat_id: str, prompt: str):
    await chat_client.update_prompt(chat_id, prompt)
