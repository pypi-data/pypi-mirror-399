from __future__ import annotations

import asyncio
import json
import os
import random
import uuid
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .providers import (
  AnthropicProvider,
  GeminiProvider,
  OpenAIProvider,
  ProviderMessage,
  get_requested_model,
  pick_provider,
)
from .sqlite_memory import SQLiteChatMemory, StoredChatMessage
from .types import (
  ChatMessage,
  ChatRequest,
  CreateConversationRequest,
  DeleteConversationRequest,
  UserOnlyRequest,
)


@dataclass
class InMemoryChatMemory:
  store: Dict[str, List[ChatMessage]]

  def get(self, user_id: str) -> List[ChatMessage]:
    return list(self.store.get(user_id, []))

  def set(self, user_id: str, messages: List[ChatMessage]) -> None:
    # Replace full history (avoids duplication when clients send full history each request).
    self.store[user_id] = list(messages)

  def clear(self, user_id: str) -> None:
    self.store.pop(user_id, None)


class MockProvider:
  name = "mock"

  def build_response(self, req: ChatRequest) -> str:
    last_user = ""
    for m in reversed(req.messages):
      if m.role == "user":
        last_user = m.content
        break
    normalized = last_user.strip() if last_user.strip() else "Say hello."

    target_chars = 1200
    include_prefix = True
    if isinstance(req.params, dict):
      mock = req.params.get("mock")
      if isinstance(mock, dict):
        try:
          target_chars = int(mock.get("targetChars", target_chars))  # type: ignore[arg-type]
        except Exception:
          target_chars = 1200
        include_prefix = bool(mock.get("includePrefix", include_prefix))

    target_chars = max(250, min(8000, target_chars))

    rng = random.Random(normalized)
    model = "mock"
    if isinstance(req.params, dict):
      m = req.params.get("model")
      if isinstance(m, str) and m.strip():
        model = m.strip()

    header = f"Mock reply ({model}): {normalized}" if include_prefix else normalized
    body = "\n\n".join(
      [
        header,
        "This is a deterministic mock response to help you test SSE token streaming.",
        "If you want a real provider, pass `params.model` like `gpt-4.1`, `claude-3-5-sonnet`, or `gemini-1.5-pro` and configure API keys.",
      ]
    )
    while len(body) < target_chars:
      body += "\n\n" + rng.choice(
        [
          "Mock streaming is useful for UI demos, cancellation tests, and load tests.",
          "For production, keep an eye on timeouts, retries, and backpressure on slow clients.",
          "If your client sends the full conversation each request, the backend should de-duplicate history. This adapter does that.",
        ]
      )
    return body

  def tokenize(self, text: str) -> List[str]:
    parts: List[str] = []
    current = ""

    def flush() -> None:
      nonlocal current
      if current:
        parts.append(current)
        current = ""

    for ch in text:
      if ch in [" ", "\n", "\t"]:
        flush()
        parts.append(ch)
      else:
        current += ch
    flush()
    return parts

  async def stream_tokens(self, req: ChatRequest, token_delay_ms: int = 10) -> AsyncGenerator[str, None]:
    delay_ms = token_delay_ms
    jitter_ms = 0
    if isinstance(req.params, dict):
      mock = req.params.get("mock")
      if isinstance(mock, dict):
        try:
          delay_ms = int(mock.get("tokenDelayMs", delay_ms))  # type: ignore[arg-type]
        except Exception:
          delay_ms = token_delay_ms
        try:
          jitter_ms = int(mock.get("jitterMs", jitter_ms))  # type: ignore[arg-type]
        except Exception:
          jitter_ms = 0

    delay_ms = max(0, min(2000, delay_ms))
    jitter_ms = max(0, min(2000, jitter_ms))

    text = self.build_response(req)
    rng = random.Random(text[:200])
    for t in self.tokenize(text):
      if delay_ms > 0 or jitter_ms > 0:
        j = rng.randint(0, jitter_ms) if jitter_ms else 0
        await asyncio.sleep((delay_ms + j) / 1000.0)
      yield t


def sse(event: str, data_obj: object) -> str:
  data = json.dumps(data_obj, ensure_ascii=False)
  return f"event: {event}\n" f"data: {data}\n\n"


def create_app(
  *,
  openai_api_key: Optional[str] = None,
  anthropic_api_key: Optional[str] = None,
  gemini_api_key: Optional[str] = None,
  sqlite_path: Optional[str] = None,
  cors_allow_origins: Optional[List[str]] = None,
) -> FastAPI:
  """
  Create a FastAPI app for SSE streaming chat.

  This library intentionally does NOT load `.env` / `.env.local`.
  Pass keys directly from your host app, or use `create_app_from_env()`.
  """

  ok_openai = bool((openai_api_key or "").strip())
  ok_anthropic = bool((anthropic_api_key or "").strip())
  ok_gemini = bool((gemini_api_key or "").strip())

  app = FastAPI(title="fastapi-ai-chat", version="0.1.0")

  app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  memory = InMemoryChatMemory(store={})

  sqlite_memory: Optional[SQLiteChatMemory]
  try:
    if sqlite_path == "":
      sqlite_memory = None
    else:
      resolved = (
        (sqlite_path or "").strip()
        or os.environ.get("FASTAPI_AI_CHAT_SQLITE_PATH")
        or os.path.join(os.getcwd(), "chat_history.sqlite3")
      )
      sqlite_memory = SQLiteChatMemory(resolved)
  except Exception:
    sqlite_memory = None

  mock_provider = MockProvider()
  openai_provider = OpenAIProvider(api_key=openai_api_key or "") if ok_openai else None
  anthropic_provider = AnthropicProvider(api_key=anthropic_api_key or "") if ok_anthropic else None
  gemini_provider = GeminiProvider(api_key=gemini_api_key or "") if ok_gemini else None

  def _get_conversation_id(req: ChatRequest) -> str:
    if isinstance(req.params, dict):
      cid = req.params.get("conversationId")
      if isinstance(cid, str) and cid.strip():
        return cid.strip()
    return uuid.uuid4().hex

  def _title_from_messages(messages: List[ChatMessage]) -> str:
    first_user = ""
    for m in messages:
      if m.role == "user":
        first_user = m.content.strip()
        break
    if not first_user:
      return "New chat"
    t = first_user.replace("\n", " ").strip()
    return t[:60] + ("…" if len(t) > 60 else "")

  @app.get("/chat/conversations")
  async def chat_conversations(userId: str, limit: int = 50):
    if sqlite_memory is None:
      return {"userId": userId, "conversations": []}
    convs = sqlite_memory.list_conversations(userId, limit=limit)
    return {
      "userId": userId,
      "conversations": [
        {
          "conversationId": c.conversation_id,
          "title": c.title,
          "createdAt": c.created_at,
          "updatedAt": c.updated_at,
          "messageCount": c.message_count,
        }
        for c in convs
      ],
    }

  @app.get("/chat/conversation")
  async def chat_conversation(userId: str, conversationId: str):
    if sqlite_memory is None:
      return {"userId": userId, "conversationId": conversationId, "messages": []}
    stored = sqlite_memory.get_conversation_messages(conversation_id=conversationId, user_id=userId)
    return {
      "userId": userId,
      "conversationId": conversationId,
      "messages": [{"role": m.role, "content": m.content, "meta": m.meta} for m in stored],
    }

  @app.post("/chat/conversation/create")
  async def chat_conversation_create(req: CreateConversationRequest):
    cid = (req.conversationId or "").strip() or uuid.uuid4().hex
    title = (req.title or "").strip() or "New chat"
    if sqlite_memory is not None:
      sqlite_memory.ensure_conversation(conversation_id=cid, user_id=req.userId, title=title)
    return {"ok": True, "userId": req.userId, "conversationId": cid, "title": title}

  @app.post("/chat/conversation/delete")
  async def chat_conversation_delete(req: DeleteConversationRequest):
    if sqlite_memory is not None:
      sqlite_memory.delete_conversation(conversation_id=req.conversationId, user_id=req.userId)
    return {"ok": True, "userId": req.userId, "conversationId": req.conversationId}

  @app.get("/chat/history")
  async def chat_history(userId: str):
    if sqlite_memory is not None:
      stored = sqlite_memory.get(userId)
      return {"userId": userId, "messages": [{"role": m.role, "content": m.content, "meta": m.meta} for m in stored]}
    msgs = memory.get(userId)
    return {"userId": userId, "messages": [m.model_dump() for m in msgs]}

  @app.post("/chat/clear")
  async def chat_clear(req: UserOnlyRequest):
    if sqlite_memory is not None:
      try:
        sqlite_memory.clear_user(req.userId)
      except Exception:
        sqlite_memory.clear(req.userId)
    else:
      memory.clear(req.userId)
    return {"ok": True, "userId": req.userId}

  @app.post("/chat/stream")
  async def chat_stream(req: ChatRequest):
    async def event_stream() -> AsyncGenerator[str, None]:
      assistant_text = ""
      try:
        conversation_id = _get_conversation_id(req)

        def to_stored(m: ChatMessage) -> StoredChatMessage:
          return StoredChatMessage(role=m.role, content=m.content, meta=m.meta)

        def same_prefix(stored: List[StoredChatMessage], incoming: List[ChatMessage]) -> bool:
          if len(stored) == 0:
            return False
          if len(incoming) < len(stored):
            return False
          for i, s in enumerate(stored):
            inc = incoming[i]
            if s.role != inc.role or s.content != inc.content:
              return False
          return True

        stored_history: List[StoredChatMessage] = []
        if sqlite_memory is not None:
          try:
            stored_history = sqlite_memory.get_conversation_messages(conversation_id=conversation_id, user_id=req.userId)
          except Exception:
            stored_history = sqlite_memory.get(req.userId)
        else:
          stored_history = [to_stored(m) for m in memory.get(req.userId)]

        if stored_history and same_prefix(stored_history, req.messages):
          merged_messages = req.messages
        else:
          merged_messages = [ChatMessage(role=m.role, content=m.content, meta=m.meta) for m in stored_history] + req.messages

        effective_req = ChatRequest(userId=req.userId, messages=merged_messages, params=req.params)

        requested_model_from_params = get_requested_model(req.params)
        requested_model = requested_model_from_params or "gpt-4.1"
        provider_used = mock_provider.name
        require_real_provider = bool(
          requested_model_from_params and not requested_model_from_params.strip().lower().startswith("mock")
        )

        try:
          which = pick_provider(requested_model)
          prov = (
            anthropic_provider
            if which == "anthropic"
            else gemini_provider
            if which == "gemini"
            else openai_provider
          )
          if prov is None:
            if require_real_provider:
              raise RuntimeError(f"Provider '{which}' is not configured (missing API key).")
            raise RuntimeError("No real provider configured; falling back to mock.")

          provider_used = prov.name
          sent_any_real_token = False
          prov_messages = [ProviderMessage(role=m.role, content=m.content) for m in effective_req.messages]
          try:
            async for token in prov.stream_tokens(model=requested_model, messages=prov_messages):
              sent_any_real_token = True
              assistant_text += token
              yield sse("token", {"type": "token", "token": token})
          except Exception as e:
            if sent_any_real_token:
              raise
            if require_real_provider:
              raise RuntimeError(f"{prov.name} failed for model '{requested_model}': {e}") from e
            provider_used = mock_provider.name
            async for token in mock_provider.stream_tokens(effective_req):
              assistant_text += token
              yield sse("token", {"type": "token", "token": token})
        except Exception:
          if require_real_provider:
            raise
          provider_used = mock_provider.name
          async for token in mock_provider.stream_tokens(effective_req):
            assistant_text += token
            yield sse("token", {"type": "token", "token": token})

        final_message = ChatMessage(role="assistant", content=assistant_text)
        full_history = merged_messages + [final_message]

        if sqlite_memory is not None:
          title = _title_from_messages(full_history)
          try:
            sqlite_memory.set_conversation_messages(
              conversation_id=conversation_id,
              user_id=req.userId,
              title=title,
              messages=[to_stored(m) for m in full_history],
            )
          except Exception:
            sqlite_memory.set(req.userId, [to_stored(m) for m in full_history])
        else:
          memory.set(req.userId, full_history)

        yield sse(
          "done",
          {
            "type": "done",
            "message": {"role": "assistant", "content": assistant_text},
            "provider": f"{provider_used}:{requested_model}",
            "usage": {"tokens": max(1, (len(assistant_text) + 3) // 4)},
            "conversationId": conversation_id,
          },
        )
      except Exception as e:
        yield sse("error", {"type": "error", "error": {"message": str(e)}})

    return StreamingResponse(event_stream(), media_type="text/event-stream")

  return app


def create_app_from_env() -> FastAPI:
  return create_app(
    openai_api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("FASTAPI_AI_CHAT_OPENAI_API_KEY"),
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("FASTAPI_AI_CHAT_ANTHROPIC_API_KEY"),
    gemini_api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("FASTAPI_AI_CHAT_GEMINI_API_KEY"),
    sqlite_path=os.environ.get("FASTAPI_AI_CHAT_SQLITE_PATH"),
  )


