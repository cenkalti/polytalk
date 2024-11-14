from typing import AsyncGenerator

import httpx
import websockets

from .chat import PROMPT

BASE_URL = "http://localhost:8000"


async def create_chat() -> str:
    url = f"{BASE_URL}/chat"
    data = {"prompt": PROMPT}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        chat_id = response.json()["id"]
        return chat_id


async def send_message(chat_id: str, name: str, message: str):
    url = f"{BASE_URL}/chat/{chat_id}/message"
    data = {"name": name, "message": message}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()


async def connect_websocket(chat_id: str, name: str) -> AsyncGenerator[str, None]:
    url = f"{BASE_URL}/chat/{chat_id}/ws/{name}"
    url = url.replace("http://", "ws://")
    url = url.replace("https://", "wss://")

    async for websocket in websockets.connect(url):
        try:
            while True:
                message = await websocket.recv()
                assert isinstance(message, str)
                yield message
        except websockets.ConnectionClosed:
            print("Connection closed. Reconnecting...")
