import asyncio

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .chat import Chat, ChatMessage

# chat id -> chat
chats: dict[str, Chat] = {}

app = FastAPI()


@app.websocket("/chat/{chat_id}/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, name: str):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    await websocket.accept()

    chat.add_participant(name, websocket)
    await chat.broadcast(f"{name} joined the chat")

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        chat.remove_participant(name)
        await chat.broadcast(f"{name} left the chat")


class CreateChatRequest(BaseModel):
    prompt: str


class CreateChatResponse(BaseModel):
    id: str


@app.post("/chat")
async def create_chat(request: CreateChatRequest):
    chat = Chat(request.prompt)
    chats[chat.id] = chat
    return CreateChatResponse(id=chat.id)


class SendMessageRequest(BaseModel):
    name: str
    message: str


@app.post("/chat/{chat_id}/message")
async def send_message(chat_id: str, request: SendMessageRequest):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    chat_message = ChatMessage(request.name, request.message)
    response = await chat.complete(chat_message)
    chat_message = ChatMessage(request.name, response)
    chat.conversation.append(chat_message)
    await chat.broadcast(f"{chat_message.user}: {chat_message.message}")


@app.get("/chat/{chat_id}/prompt")
async def get_prompt(chat_id: str):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    return chat.prompt


@app.post("/chat/{chat_id}/prompt")
async def update_prompt(chat_id: str, request: CreateChatRequest):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    chat.prompt = request.prompt
