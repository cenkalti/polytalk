# duologue

Duologue is a simple chat app for LLM mediated human conversations.

## UX
- user opens http://localhost:8000
- user enters a prompt
- user submits the prompt
- user is redirected to http://localhost:8000/<channel_id>
- user enters a name
- user submits the name
- user starts chatting

## Architecture
- FastAPI for backend
- Daisy UI for tailwind components
- HTMX for interactivity
- WebSockets for real-time communication
- Prompts, channel IDs and messages are stored in SQLite
