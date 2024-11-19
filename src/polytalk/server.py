import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .chat import Chat, ChatMessage

# chat id -> chat
chats: dict[str, Chat] = {}


def get_chat(chat_id: str) -> Chat:
    try:
        return chats[chat_id]
    except KeyError:
        chat = Chat()
        chats[chat_id] = chat
        return chat


app = FastAPI()


@app.websocket("/chat/{chat_id}/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, name: str):
    await websocket.accept()

    chat = get_chat(chat_id)
    chat.add_participant(name, websocket)
    await chat.broadcast(f"{name} joined the chat")

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        chat.remove_participant(name)
        await chat.broadcast(f"{name} left the chat")


class SendMessageRequest(BaseModel):
    name: str
    message: str


@app.post("/chat/{chat_id}/message")
async def send_message(chat_id: str, request: SendMessageRequest):
    chat = get_chat(chat_id)
    chat_message = ChatMessage(user=request.name, message=request.message)
    response = await chat.complete(chat_message)
    for message in response:
        chat.conversation.append(message)
        await chat.broadcast(f"{message.user}: {message.message}")


@app.get("/chat/{chat_id}/prompt")
async def get_prompt(chat_id: str):
    chat = get_chat(chat_id)
    return chat.prompt


class UpdatePromptRequest(BaseModel):
    prompt: str


@app.post("/chat/{chat_id}/prompt")
async def update_prompt(chat_id: str, request: UpdatePromptRequest):
    chat = get_chat(chat_id)
    chat.prompt = request.prompt
