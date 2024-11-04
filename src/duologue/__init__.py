import os
from dataclasses import dataclass

import requests
import typer
import uvicorn
from fastapi import FastAPI, Response
from openai import AzureOpenAI
from pydantic import BaseModel

PROMPT = """
You are a mediator between 2 humans chatting.

Your goal is to analyze the conversation and next user's message to determine what message to add to the conversation.

You should always respond with the modified last message in the conversation.

Example:
<conversation>
alice: Hi Bob?
bob: Hi Alice.
</conversation>

<last_message>
User name: alice
User message: What the fuck are you doing here?
</last_message>

Answer:
alice: What are you doing here?
"""

# TODO: Replace this with LiteLLM
llm = AzureOpenAI()


@dataclass
class ChatMessage:
    user: str
    message: str


class Chat:
    def __init__(self, prompt: str):
        self.id = os.urandom(4).hex()
        self.prompt = prompt
        self.conversation: list[ChatMessage] = []

    def complete(self, chat_message: ChatMessage):
        conversation = "\n".join([f"{message.user}: {message.message}" for message in self.conversation])
        last_message = f"User name: {chat_message.user}\nUser message: {chat_message.message}"
        user_message = (
            f"<conversation>\n{conversation}\n</conversation>\n<last_message>\n{last_message}\n</last_message>"
        )
        print(user_message)
        completion = llm.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": user_message},
            ],
        )
        answer = completion.choices[0].message.content
        print(f"Answer: {answer}")
        assert isinstance(answer, str)
        return answer


chats = {}

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


@app.post("/chat/{chat_id}/message")
async def send_message(chat_id: str, request: SendMessageRequest):
    if chat_id not in chats:
        return Response(status_code=404, content="Chat not found")

    chat = chats[chat_id]
    chat_message = ChatMessage(request.name, request.message)
    response = chat.complete(chat_message)
    chat_message = ChatMessage(request.name, response)
    chat.conversation.append(chat_message)
    return {"message": response}


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


if __name__ == "__main__":
    cli()
