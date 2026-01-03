from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StoredChatMessage:
  role: str
  content: str
  meta: Optional[Dict[str, object]] = None


@dataclass(frozen=True)
class StoredConversation:
  conversation_id: str
  user_id: str
  title: str
  created_at: int
  updated_at: int
  message_count: int


class SQLiteChatMemory:
  """
  SQLite-backed conversation store.

  Tables:
  - `conversations`: one row per conversation (chat)
  - `conversation_messages`: one row per message within a conversation, ordered by idx

  For correctness with clients that send the full conversation each request, we support
  `set_conversation_messages(...)` which replaces the entire message list atomically.
  """

  def __init__(self, db_path: str):
    self.db_path = db_path
    self._init_db()

  def _connect(self) -> sqlite3.Connection:
    con = sqlite3.connect(self.db_path)
    con.row_factory = sqlite3.Row
    return con

  def _init_db(self) -> None:
    with self._connect() as con:
      con.execute("PRAGMA journal_mode=WAL;")
      con.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
          conversation_id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          title TEXT NOT NULL,
          created_at INTEGER NOT NULL DEFAULT (unixepoch()),
          updated_at INTEGER NOT NULL DEFAULT (unixepoch())
        );
        """
      )
      con.execute("CREATE INDEX IF NOT EXISTS conversations_user ON conversations (user_id, updated_at DESC);")

      con.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_messages (
          conversation_id TEXT NOT NULL,
          idx INTEGER NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          meta_json TEXT NULL,
          created_at INTEGER NOT NULL DEFAULT (unixepoch()),
          PRIMARY KEY (conversation_id, idx),
          FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
        );
        """
      )
      con.execute("CREATE INDEX IF NOT EXISTS conv_messages_conv ON conversation_messages (conversation_id, idx);")
      con.execute("PRAGMA foreign_keys=ON;")

  def ensure_conversation(self, *, conversation_id: str, user_id: str, title: str) -> None:
    with self._connect() as con:
      con.execute("BEGIN")
      row = con.execute(
        "SELECT conversation_id FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
      ).fetchone()
      if row is None:
        con.execute(
          "INSERT INTO conversations (conversation_id, user_id, title) VALUES (?, ?, ?)",
          (conversation_id, user_id, title),
        )
      else:
        con.execute(
          "UPDATE conversations SET updated_at = unixepoch() WHERE conversation_id = ?",
          (conversation_id,),
        )
      con.execute("COMMIT")

  def list_conversations(self, user_id: str, limit: int = 50) -> List[StoredConversation]:
    with self._connect() as con:
      rows = con.execute(
        """
        SELECT
          c.conversation_id,
          c.user_id,
          c.title,
          c.created_at,
          c.updated_at,
          (
            SELECT COUNT(1)
            FROM conversation_messages m
            WHERE m.conversation_id = c.conversation_id
          ) AS message_count
        FROM conversations c
        WHERE c.user_id = ?
        ORDER BY c.updated_at DESC
        LIMIT ?;
        """,
        (user_id, int(limit)),
      ).fetchall()

      out: List[StoredConversation] = []
      for r in rows:
        out.append(
          StoredConversation(
            conversation_id=str(r["conversation_id"]),
            user_id=str(r["user_id"]),
            title=str(r["title"]),
            created_at=int(r["created_at"]),
            updated_at=int(r["updated_at"]),
            message_count=int(r["message_count"] or 0),
          )
        )
      return out

  def get_conversation_messages(self, *, conversation_id: str, user_id: str) -> List[StoredChatMessage]:
    with self._connect() as con:
      owner = con.execute(
        "SELECT user_id FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
      ).fetchone()
      if owner is None or str(owner["user_id"]) != user_id:
        return []

      rows = con.execute(
        "SELECT role, content, meta_json FROM conversation_messages WHERE conversation_id = ? ORDER BY idx ASC",
        (conversation_id,),
      ).fetchall()
      out: List[StoredChatMessage] = []
      for r in rows:
        meta_json = r["meta_json"]
        meta: Optional[Dict[str, object]] = None
        if isinstance(meta_json, str) and meta_json.strip():
          try:
            parsed = json.loads(meta_json)
            if isinstance(parsed, dict):
              meta = parsed  # type: ignore[assignment]
          except Exception:
            meta = None
        out.append(StoredChatMessage(role=str(r["role"]), content=str(r["content"]), meta=meta))
      return out

  def set_conversation_messages(
    self,
    *,
    conversation_id: str,
    user_id: str,
    title: str,
    messages: List[StoredChatMessage],
  ) -> None:
    with self._connect() as con:
      con.execute("BEGIN")
      row = con.execute(
        "SELECT user_id FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
      ).fetchone()
      if row is None:
        con.execute(
          "INSERT INTO conversations (conversation_id, user_id, title) VALUES (?, ?, ?)",
          (conversation_id, user_id, title),
        )
      else:
        if str(row["user_id"]) != user_id:
          con.execute("ROLLBACK")
          return
        con.execute(
          "UPDATE conversations SET title = ?, updated_at = unixepoch() WHERE conversation_id = ?",
          (title, conversation_id),
        )

      con.execute("DELETE FROM conversation_messages WHERE conversation_id = ?", (conversation_id,))
      con.executemany(
        "INSERT INTO conversation_messages (conversation_id, idx, role, content, meta_json) VALUES (?, ?, ?, ?, ?)",
        [
          (
            conversation_id,
            i,
            m.role,
            m.content,
            json.dumps(m.meta, ensure_ascii=False) if isinstance(m.meta, dict) else None,
          )
          for i, m in enumerate(messages)
        ],
      )
      con.execute("COMMIT")

  def delete_conversation(self, *, conversation_id: str, user_id: str) -> None:
    with self._connect() as con:
      con.execute("BEGIN")
      row = con.execute(
        "SELECT user_id FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
      ).fetchone()
      if row is None or str(row["user_id"]) != user_id:
        con.execute("ROLLBACK")
        return
      con.execute("DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,))
      con.execute("COMMIT")

  def clear_user(self, user_id: str) -> None:
    with self._connect() as con:
      con.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))

  # ---------------------------------------------------------------------------
  # Backwards-compatible single-thread "legacy" API (used by older clients)
  # ---------------------------------------------------------------------------

  def _legacy_conversation_id(self, user_id: str) -> str:
    return f"default:{user_id}"

  def get(self, user_id: str) -> List[StoredChatMessage]:
    cid = self._legacy_conversation_id(user_id)
    return self.get_conversation_messages(conversation_id=cid, user_id=user_id)

  def set(self, user_id: str, messages: List[StoredChatMessage]) -> None:
    cid = self._legacy_conversation_id(user_id)
    self.set_conversation_messages(conversation_id=cid, user_id=user_id, title="Chat", messages=messages)

  def clear(self, user_id: str) -> None:
    cid = self._legacy_conversation_id(user_id)
    self.delete_conversation(conversation_id=cid, user_id=user_id)


