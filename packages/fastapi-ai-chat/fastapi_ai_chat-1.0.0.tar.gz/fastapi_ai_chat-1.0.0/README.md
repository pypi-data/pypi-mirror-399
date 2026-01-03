## fastapi-ai-chat

Minimal FastAPI backend for **streaming AI chat over Server‑Sent Events (SSE)**.

It’s designed to be wire‑compatible with `ai-chat-kit`’s React FastAPI adapter:
- `POST /chat/stream` returns `text/event-stream`
- emits SSE events: `token`, `done`, `error`

### Features

- **Token streaming over SSE**: incremental `token` events + final `done` event (or `error`).
- **Provider routing by model name**:
  - OpenAI for most models (default: `gpt-4.1`)
  - Anthropic for models starting with `claude`
  - Gemini for models starting with `gemini`
- **Mock streaming fallback**: deterministic mock stream when no provider keys are configured (great for UI/dev).
- **Conversation persistence (optional)**: SQLite chat history + basic conversation CRUD endpoints.
- **CORS enabled**: defaults to `*` for local dev (configurable).

### Install

From PyPI:

```bash
python -m pip install "fastapi-ai-chat[server]"
```

### Quickstart (run the example server)

```bash
cd Backend/fastapi-ai-chat
python -m uvicorn examples.server:app --reload --port 8000
```

### Configuration (environment variables)

This library intentionally does **not** load `.env` files for you; it reads process env vars (or you can pass keys directly to `create_app(...)`).

- **Provider keys**
  - `OPENAI_API_KEY` or `FASTAPI_AI_CHAT_OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY` or `FASTAPI_AI_CHAT_ANTHROPIC_API_KEY`
  - `GEMINI_API_KEY` or `FASTAPI_AI_CHAT_GEMINI_API_KEY`
- **Persistence**
  - `FASTAPI_AI_CHAT_SQLITE_PATH` (default: `./chat_history.sqlite3`)
- **Optional provider base URL overrides**
  - `OPENAI_BASE_URL` / `FASTAPI_AI_CHAT_OPENAI_BASE_URL`
  - `ANTHROPIC_BASE_URL` / `FASTAPI_AI_CHAT_ANTHROPIC_BASE_URL`
  - `GEMINI_BASE_URL` / `FASTAPI_AI_CHAT_GEMINI_BASE_URL`

### Example use

#### 1) Stream tokens (curl)

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "userId":"u1",
    "messages":[{"role":"user","content":"Hello streaming"}]
  }'
```

#### 2) Pick a real model/provider

Send `params.model` in the request body:
- OpenAI: `gpt-4.1` (default if omitted)
- Anthropic: `claude-3-5-sonnet` (or any model starting with `claude`)
- Gemini: `gemini-1.5-pro` (or any model starting with `gemini`)

Example:

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "userId":"u1",
    "messages":[{"role":"user","content":"Write a haiku about SSE."}],
    "params":{"model":"gpt-4.1"}
  }'
```

If you don’t configure provider keys, the backend falls back to a deterministic mock stream **unless** a real model was explicitly requested via `params.model`.

#### 3) Embed in your own FastAPI app

```python
from fastapi_ai_chat import create_app_from_env

app = create_app_from_env()
```

Or pass configuration explicitly:

```python
from fastapi_ai_chat import create_app

app = create_app(
    openai_api_key="...",  # or None / "" to disable OpenAI
    anthropic_api_key="...",
    gemini_api_key="...",
    sqlite_path="./chat_history.sqlite3",
    cors_allow_origins=["http://localhost:5173"],
)
```

### API

#### Streaming protocol (SSE)

The server emits frames separated by a blank line (`\n\n`):
- `event: token` with JSON: `{"type":"token","token":"..."}` (many times)
- `event: done` with JSON:
  - `{"type":"done","message":{"role":"assistant","content":"..."}, "provider":"...", "usage":{...}, "conversationId":"..."}`
- `event: error` with JSON: `{"type":"error","error":{"message":"..."}}`

#### Endpoints

- `POST /chat/stream`: stream assistant tokens (SSE)
- `GET /chat/history?userId=...`: get message history for a user
- `POST /chat/clear`: clear a user’s history
- `GET /chat/conversations?userId=...`: list conversations (SQLite mode)
- `GET /chat/conversation?userId=...&conversationId=...`: fetch one conversation (SQLite mode)
- `POST /chat/conversation/create`: create/ensure a conversation (SQLite mode)
- `POST /chat/conversation/delete`: delete a conversation (SQLite mode)

### Publish to PyPI (maintainers)

Build:

```bash
python -m pip install -U build twine
python -m build Backend/fastapi-ai-chat
```

Upload:
- Recommended: PyPI Trusted Publishing
- Or token-based:

```bash
python -m twine upload Backend/fastapi-ai-chat/dist/*
```

### Author

- Name: Shrikant Jagtap
- Email: shrijagtap11@gmail.com


