import os
from datetime import datetime
from typing import Protocol

from openai import AsyncAzureOpenAI
from pydantic import BaseModel

INITIAL_PROMPT = """
You are a participant is a group chat.
You only communicate in English.
Your name is Poly. Others may refer to you as Poly or @poly.
Only reply as Poly if you are asked specifically to do so by mentioning your name, otherwise say nothing as Poly.
You have ability to intercept messages and modify them.
Current date and time is {date}.
Your goal is to analyze the conversation and last message to determine what message(s) to add to the conversation.

Example 1:

<conversation>
alice: Hi Bob.
bob: Hi Alice.
</conversation>

<last_message>
alice: what the fuck are you doin here
</last_message>

<response>
alice: What are you doing here?
</response>

Example 2:

<conversation>
</conversation>

<last_message>
alice: what time is it poly
</last_message>

<response>
alice: What time is it Poly?
poly: It's 12:00 PM.
</response>

Example 3:

<conversation>
</conversation>

<last_message>
alice: what time is it
</last_message>

<response>
alice: What time is it?
[no poly response here]
</response>

Additinal instructions:
- Add appropriate emojis based on message content
"""

llm = AsyncAzureOpenAI()


class ChatMessage(BaseModel):
    user: str
    message: str


class ChatConnection(Protocol):
    async def send_text(self, data: str) -> None: ...


class Chat:
    def __init__(self):
        self.prompt = INITIAL_PROMPT
        self.conversation: list[ChatMessage] = []
        self.participants: dict[str, ChatConnection] = {}

    async def complete(self, chat_message: ChatMessage) -> list[ChatMessage]:
        class Response(BaseModel):
            messages: list[ChatMessage]

        conversation = "\n".join([f"{message.user}: {message.message}" for message in self.conversation])
        last_message = f"User name: {chat_message.user}\nUser message: {chat_message.message}"
        user_message = (
            f"<conversation>\n{conversation}\n</conversation>\n<last_message>\n{last_message}\n</last_message>"
        )
        print(f"Conversation:\n{user_message}")
        response = await llm.beta.chat.completions.parse(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            response_format=Response,
            messages=[
                {"role": "system", "content": self.prompt.format(date=str(datetime.now()))},
                {"role": "user", "content": user_message},
            ],
        )
        user_message = response.choices[0].message.parsed
        print(f"Response:\n{user_message}")
        assert isinstance(user_message, Response)
        return user_message.messages

    def add_participant(self, name: str, connection: ChatConnection):
        self.participants[name] = connection

    def remove_participant(self, name: str):
        del self.participants[name]

    async def broadcast(self, message: str):
        for connection in self.participants.values():
            await connection.send_text(message)
