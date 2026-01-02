from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
  role: Role
  content: str
  meta: Optional[Dict[str, object]] = None


class ChatRequest(BaseModel):
  userId: str = Field(..., min_length=1)
  messages: List[ChatMessage]
  params: Optional[Dict[str, object]] = None


class UserOnlyRequest(BaseModel):
  userId: str = Field(..., min_length=1)


class DeleteConversationRequest(BaseModel):
  userId: str = Field(..., min_length=1)
  conversationId: str = Field(..., min_length=1)


class CreateConversationRequest(BaseModel):
  userId: str = Field(..., min_length=1)
  conversationId: Optional[str] = None
  title: Optional[str] = None


