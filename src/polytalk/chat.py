import os
import random
from dataclasses import dataclass
from typing import Protocol

from openai import AsyncAzureOpenAI
from pydantic import BaseModel

# TODO: Replace this
PROMPT = """
You are a mediator between 2 humans chatting.

Your goal is to analyze the conversation and next user's message to determine what message to add to the conversation.

You should always respond with the modified last message in the conversation.

Example:

<conversation>
alice: Hi Bob.
bob: Hi Alice.
</conversation>

<last_message>
User name: alice
User message: what the fuck are you doin here
</last_message>

Answer:
alice: What are you doing here?

Additinal instructions:
Enhance each message with appropriate emojis that amplify the emotional content and meaning,
while maintaining the original text. Add 2-4 relevant emojis per message.
"""

llm = AsyncAzureOpenAI()


@dataclass
class ChatMessage:
    user: str
    message: str


class ChatConnection(Protocol):
    async def send_text(self, data: str) -> None: ...


class Chat:
    def __init__(self, prompt: str):
        self.id = f"{random.randint(0, 9999):04}"
        self.prompt = prompt
        self.conversation: list[ChatMessage] = []
        self.participants: dict[str, ChatConnection] = {}

    async def complete(self, chat_message: ChatMessage):
        class UserMessage(BaseModel):
            user: str
            message: str

        conversation = "\n".join([f"{message.user}: {message.message}" for message in self.conversation])
        last_message = f"User name: {chat_message.user}\nUser message: {chat_message.message}"
        user_message = (
            f"<conversation>\n{conversation}\n</conversation>\n<last_message>\n{last_message}\n</last_message>"
        )
        print(f"Conversation:\n{user_message}")
        response = await llm.beta.chat.completions.parse(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            response_format=UserMessage,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": user_message},
            ],
        )
        user_message = response.choices[0].message.parsed
        print(f"Response:\n{user_message}")
        assert isinstance(user_message, UserMessage)
        return user_message.message

    def add_participant(self, name: str, connection: ChatConnection):
        self.participants[name] = connection

    def remove_participant(self, name: str):
        del self.participants[name]

    async def broadcast(self, message: str):
        for connection in self.participants.values():
            await connection.send_text(message)
