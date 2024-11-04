import os
from dataclasses import dataclass

from openai import AzureOpenAI

# TODO: Replace this
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
