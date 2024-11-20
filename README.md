# polytalk

Polytalk is a simple chat app for LLM mediated human conversations.

## Features
- Poly chatbot participates in the conversation
- Can intercept messages and replace with LLM responses

## Usage

Run server:
```
pdm run python3 -m polytalk.cli server
```

Run client:
```
pdm run python3 -m polytalk.cli client alice <chat_id>
pdm run python3 -m polytalk.cli client bob   <chat_id>
```
