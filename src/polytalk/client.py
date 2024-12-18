from typing import AsyncGenerator

import httpx
import websockets

BASE_URL = "http://localhost:8000"


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


async def get_prompt(chat_id: str) -> str:
    url = f"{BASE_URL}/chat/{chat_id}/prompt"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def update_prompt(chat_id: str, prompt: str):
    url = f"{BASE_URL}/chat/{chat_id}/prompt"
    data = {"prompt": prompt}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
