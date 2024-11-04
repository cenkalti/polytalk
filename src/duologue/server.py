from fastapi import FastAPI, Response
from pydantic import BaseModel

from .chat import Chat, ChatMessage, chats

app = FastAPI()


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


class SendMessageResponse(BaseModel):
    message: str


@app.post("/chat/{chat_id}/message")
async def send_message(chat_id: str, request: SendMessageRequest):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    chat_message = ChatMessage(request.name, request.message)
    response = chat.complete(chat_message)
    chat_message = ChatMessage(request.name, response)
    chat.conversation.append(chat_message)
    return SendMessageResponse(message=response)
