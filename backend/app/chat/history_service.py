"""Persistence for conversation history, separate from personal memories."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from app.config import DEMO_USER_ID
from app.models.database import db_cursor
from app.models.schemas import ChatHistoryMessage

ChatRole = Literal["user", "assistant"]


def _new_message(role: ChatRole, content: str, timestamp: datetime) -> ChatHistoryMessage:
    return ChatHistoryMessage(
        id=str(uuid.uuid4()),
        role=role,
        content=content,
        timestamp=timestamp,
    )


def _insert_message(cur, message: ChatHistoryMessage) -> None:
    cur.execute(
        "INSERT INTO chat_messages (id, user_id, role, content, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            message.id,
            DEMO_USER_ID,
            message.role,
            message.content,
            message.timestamp.isoformat(),
        ),
    )


def save_message(role: ChatRole, content: str) -> ChatHistoryMessage:
    message = _new_message(role, content, datetime.now(timezone.utc))
    with db_cursor() as cur:
        _insert_message(cur, message)
    return message


def save_exchange(user_content: str, assistant_content: str) -> None:
    """Save both messages atomically after a successful model response."""

    user_timestamp = datetime.now(timezone.utc)
    user_message = _new_message("user", user_content, user_timestamp)
    assistant_message = _new_message(
        "assistant", assistant_content, user_timestamp + timedelta(microseconds=1)
    )
    with db_cursor() as cur:
        _insert_message(cur, user_message)
        _insert_message(cur, assistant_message)


def get_history() -> list[ChatHistoryMessage]:
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, role, content, timestamp FROM chat_messages "
            "WHERE user_id = ? ORDER BY timestamp ASC, rowid ASC",
            (DEMO_USER_ID,),
        )
        rows = cur.fetchall()
    return [
        ChatHistoryMessage(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            timestamp=row["timestamp"],
        )
        for row in rows
    ]


def clear_history() -> int:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM chat_messages WHERE user_id = ?", (DEMO_USER_ID,))
        count = cur.fetchone()["count"]
        cur.execute("DELETE FROM chat_messages WHERE user_id = ?", (DEMO_USER_ID,))
    return count