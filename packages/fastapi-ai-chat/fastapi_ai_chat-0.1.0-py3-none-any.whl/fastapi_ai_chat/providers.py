from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Literal, Optional, Sequence, Tuple

Role = Literal["system", "user", "assistant"]


@dataclass
class ProviderMessage:
  role: Role
  content: str


def _env(*names: str) -> str:
  for n in names:
    v = os.environ.get(n)
    if isinstance(v, str) and v.strip():
      return v.strip()
  return ""


def get_requested_model(params: Optional[Dict[str, object]]) -> str:
  if isinstance(params, dict):
    m = params.get("model")
    if isinstance(m, str) and m.strip():
      return m.strip()
  return ""


def normalize_provider_messages(messages: Sequence[ProviderMessage]) -> Tuple[str, List[Dict[str, str]]]:
  """
  Convert messages into:
  - a single system prompt (concatenated), and
  - a chat messages list with only user/assistant roles.
  """
  system_parts: List[str] = []
  chat: List[Dict[str, str]] = []
  for m in messages:
    if m.role == "system":
      if m.content.strip():
        system_parts.append(m.content.strip())
      continue
    if m.role in ("user", "assistant"):
      chat.append({"role": m.role, "content": m.content})
  return ("\n\n".join(system_parts).strip(), chat)


class ProviderError(RuntimeError):
  pass


class BaseProvider:
  name: str

  async def stream_tokens(self, *, model: str, messages: Sequence[ProviderMessage]) -> AsyncGenerator[str, None]:
    raise NotImplementedError


class OpenAIProvider(BaseProvider):
  name = "openai"

  def __init__(self, *, api_key: str) -> None:
    self.api_key = (api_key or "").strip()
    self.base_url = _env("OPENAI_BASE_URL", "FASTAPI_AI_CHAT_OPENAI_BASE_URL") or "https://api.openai.com/v1"
    try:
      self.max_retries = int(_env("FASTAPI_AI_CHAT_OPENAI_MAX_RETRIES") or "2")
    except Exception:
      self.max_retries = 2
    try:
      self.retry_base_delay_ms = int(_env("FASTAPI_AI_CHAT_OPENAI_RETRY_BASE_DELAY_MS") or "500")
    except Exception:
      self.retry_base_delay_ms = 500
    try:
      self.retry_max_delay_ms = int(_env("FASTAPI_AI_CHAT_OPENAI_RETRY_MAX_DELAY_MS") or "8000")
    except Exception:
      self.retry_max_delay_ms = 8000

  async def stream_tokens(self, *, model: str, messages: Sequence[ProviderMessage]) -> AsyncGenerator[str, None]:
    if not self.api_key:
      raise ProviderError("Missing OPENAI_API_KEY (or FASTAPI_AI_CHAT_OPENAI_API_KEY)")

    try:
      import httpx  # type: ignore
    except Exception as e:  # pragma: no cover
      raise ProviderError("Missing dependency: httpx (pip install httpx)") from e

    system, chat_messages = normalize_provider_messages(messages)
    if system:
      chat_messages = [{"role": "system", "content": system}] + chat_messages

    url = f"{self.base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": chat_messages, "stream": True}

    timeout = httpx.Timeout(connect=20.0, read=120.0, write=20.0, pool=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
      attempt = 0
      while True:
        try:
          async with client.stream("POST", url, headers=headers, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
              if not line:
                continue
              if line.startswith("data:"):
                data = line[len("data:") :].strip()
              else:
                continue
              if data == "[DONE]":
                return
              try:
                payload = json.loads(data)
              except Exception:
                continue
              try:
                delta = payload["choices"][0].get("delta", {})
                piece = delta.get("content")
              except Exception:
                piece = None
              if isinstance(piece, str) and piece:
                yield piece
            return
        except Exception as e:
          status = None
          retry_after_s = None
          try:
            resp = getattr(e, "response", None)
            status = int(getattr(resp, "status_code", 0) or 0)
            if resp is not None:
              ra = resp.headers.get("retry-after")
              if isinstance(ra, str) and ra.strip():
                try:
                  retry_after_s = float(ra.strip())
                except Exception:
                  retry_after_s = None
          except Exception:
            status = None

          retryable = status in (429, 500, 502, 503, 504)
          if not retryable or attempt >= max(0, self.max_retries):
            raise

          backoff_ms = min(self.retry_max_delay_ms, int(self.retry_base_delay_ms * (2**attempt)))
          delay_s = max((backoff_ms / 1000.0), (retry_after_s or 0.0))
          delay_s = delay_s + (0.05 * (attempt + 1))
          attempt += 1
          await asyncio.sleep(delay_s)


class AnthropicProvider(BaseProvider):
  name = "anthropic"

  def __init__(self, *, api_key: str) -> None:
    self.api_key = (api_key or "").strip()
    self.base_url = _env("ANTHROPIC_BASE_URL", "FASTAPI_AI_CHAT_ANTHROPIC_BASE_URL") or "https://api.anthropic.com/v1"
    self.model_map = {
      "claude-3.5-sonnet": "claude-3-5-sonnet-latest",
      "claude-3-5-sonnet": "claude-3-5-sonnet-latest",
    }

  def _map_model(self, model: str) -> str:
    return self.model_map.get(model, model)

  async def stream_tokens(self, *, model: str, messages: Sequence[ProviderMessage]) -> AsyncGenerator[str, None]:
    if not self.api_key:
      raise ProviderError("Missing ANTHROPIC_API_KEY (or FASTAPI_AI_CHAT_ANTHROPIC_API_KEY)")

    try:
      import httpx  # type: ignore
    except Exception as e:  # pragma: no cover
      raise ProviderError("Missing dependency: httpx (pip install httpx)") from e

    system, chat_messages = normalize_provider_messages(messages)

    url = f"{self.base_url.rstrip('/')}/messages"
    headers = {
      "x-api-key": self.api_key,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    }
    body: Dict[str, object] = {"model": self._map_model(model), "max_tokens": 1024, "messages": chat_messages, "stream": True}
    if system:
      body["system"] = system

    timeout = httpx.Timeout(connect=20.0, read=120.0, write=20.0, pool=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
      async with client.stream("POST", url, headers=headers, json=body) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
          if not line:
            continue
          if not line.startswith("data:"):
            continue
          data = line[len("data:") :].strip()
          if not data:
            continue
          try:
            payload = json.loads(data)
          except Exception:
            continue
          typ = payload.get("type")
          if typ == "content_block_delta":
            delta = payload.get("delta") or {}
            text = delta.get("text")
            if isinstance(text, str) and text:
              yield text
          elif typ == "message_stop":
            break


class GeminiProvider(BaseProvider):
  name = "gemini"

  def __init__(self, *, api_key: str) -> None:
    self.api_key = (api_key or "").strip()
    self.base_url = _env("GEMINI_BASE_URL", "FASTAPI_AI_CHAT_GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta"
    try:
      self.max_retries = int(_env("FASTAPI_AI_CHAT_GEMINI_MAX_RETRIES") or "2")
    except Exception:
      self.max_retries = 2
    try:
      self.retry_base_delay_ms = int(_env("FASTAPI_AI_CHAT_GEMINI_RETRY_BASE_DELAY_MS") or "500")
    except Exception:
      self.retry_base_delay_ms = 500
    try:
      self.retry_max_delay_ms = int(_env("FASTAPI_AI_CHAT_GEMINI_RETRY_MAX_DELAY_MS") or "8000")
    except Exception:
      self.retry_max_delay_ms = 8000

  def _to_gemini_contents(self, messages: Sequence[ProviderMessage]) -> Tuple[Optional[Dict[str, object]], List[Dict[str, object]]]:
    system, chat = normalize_provider_messages(messages)
    system_instruction: Optional[Dict[str, object]] = None
    if system:
      system_instruction = {"parts": [{"text": system}]}

    contents: List[Dict[str, object]] = []
    for m in chat:
      role = "user" if m.get("role") == "user" else "model"
      text = str(m.get("content") or "")
      contents.append({"role": role, "parts": [{"text": text}]})
    return system_instruction, contents

  def _extract_text(self, payload: object) -> str:
    if not isinstance(payload, dict):
      return ""
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
      return ""
    c0 = candidates[0]
    if not isinstance(c0, dict):
      return ""
    content = c0.get("content")
    if not isinstance(content, dict):
      return ""
    parts = content.get("parts")
    if not isinstance(parts, list) or not parts:
      return ""
    out: List[str] = []
    for p in parts:
      if isinstance(p, dict):
        t = p.get("text")
        if isinstance(t, str) and t:
          out.append(t)
    return "".join(out)

  async def stream_tokens(self, *, model: str, messages: Sequence[ProviderMessage]) -> AsyncGenerator[str, None]:
    if not self.api_key:
      raise ProviderError("Missing GEMINI_API_KEY (or FASTAPI_AI_CHAT_GEMINI_API_KEY)")

    try:
      import httpx  # type: ignore
    except Exception as e:  # pragma: no cover
      raise ProviderError("Missing dependency: httpx (pip install httpx)") from e

    system_instruction, contents = self._to_gemini_contents(messages)

    base = self.base_url.rstrip("/")
    url = f"{base}/models/{model}:streamGenerateContent"
    params = {"key": self.api_key, "alt": "sse"}
    headers = {"Content-Type": "application/json"}
    body: Dict[str, object] = {"contents": contents}
    if system_instruction:
      body["systemInstruction"] = system_instruction

    timeout = httpx.Timeout(connect=20.0, read=120.0, write=20.0, pool=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
      attempt = 0
      prev_text = ""
      while True:
        try:
          async with client.stream("POST", url, headers=headers, params=params, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
              if not line:
                continue
              if line.startswith("data:"):
                data = line[len("data:") :].strip()
              else:
                continue
              if not data:
                continue
              if data == "[DONE]":
                return
              try:
                payload = json.loads(data)
              except Exception:
                continue

              text = self._extract_text(payload)
              if not isinstance(text, str) or not text:
                continue

              if prev_text and text.startswith(prev_text):
                piece = text[len(prev_text) :]
              else:
                piece = text
              prev_text = text
              if piece:
                yield piece
            return
        except Exception as e:
          status = None
          retry_after_s = None
          try:
            resp = getattr(e, "response", None)
            status = int(getattr(resp, "status_code", 0) or 0)
            if resp is not None:
              ra = resp.headers.get("retry-after")
              if isinstance(ra, str) and ra.strip():
                try:
                  retry_after_s = float(ra.strip())
                except Exception:
                  retry_after_s = None
          except Exception:
            status = None

          retryable = status in (429, 500, 502, 503, 504)
          if not retryable or attempt >= max(0, self.max_retries):
            raise

          backoff_ms = min(self.retry_max_delay_ms, int(self.retry_base_delay_ms * (2**attempt)))
          delay_s = max((backoff_ms / 1000.0), (retry_after_s or 0.0))
          delay_s = delay_s + (0.05 * (attempt + 1))
          attempt += 1
          await asyncio.sleep(delay_s)


def pick_provider(model: str) -> str:
  m = (model or "").strip().lower()
  if m.startswith("gemini"):
    return "gemini"
  if m.startswith("claude"):
    return "anthropic"
  return "openai"


