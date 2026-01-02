## fastapi-ai-chat

Minimal FastAPI backend library for **streaming AI chat over Server-Sent Events (SSE)**.

Designed to be wire-compatible with `ai-chat-kit`'s React adapter:
- `POST /chat/stream` returns `text/event-stream`
- emits SSE events: `token`, `done`, `error`

### Install

Local editable install (recommended during development):

```bash
python -m pip install -e Backend/fastapi-ai-chat
```

From PyPI (after you publish):

```bash
python -m pip install "fastapi-ai-chat[server]"
```

### Run

Create a small server file (or use the included example):

```bash
python -m pip install "fastapi-ai-chat[server]"
python -m uvicorn examples.server:app --reload --port 8000
```

Environment variables (optional):
- `OPENAI_API_KEY` or `FASTAPI_AI_CHAT_OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` or `FASTAPI_AI_CHAT_ANTHROPIC_API_KEY`
- `GEMINI_API_KEY` or `FASTAPI_AI_CHAT_GEMINI_API_KEY`
- `FASTAPI_AI_CHAT_SQLITE_PATH` (default: `./chat_history.sqlite3`)

### Streaming protocol (SSE)

The server emits frames separated by a blank line (`\n\n`):
- `event: token` with JSON: `{"type":"token","token":"..."}` (many times)
- `event: done` with JSON: `{"type":"done","message":{"role":"assistant","content":"..."}, "provider":"...", "conversationId":"..."}`
- `event: error` with JSON: `{"type":"error","error":{"message":"..."}}`

Test streaming:

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"userId":"u1","messages":[{"role":"user","content":"Hello streaming"}]}'
```

### Selecting a model/provider

Send `params.model` in the request body:
- OpenAI: `gpt-4.1` (default if omitted)
- Anthropic: `claude-3-5-sonnet` (or any model starting with `claude`)
- Gemini: `gemini-1.5-pro` (or any model starting with `gemini`)

If you do **not** configure provider keys, the backend will fall back to a deterministic mock stream unless a real model was explicitly requested.

### Publish to PyPI

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


