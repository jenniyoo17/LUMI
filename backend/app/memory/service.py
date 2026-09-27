"""Personal memory storage.

Memories are always stored regardless of the current permission state of
their source — disabling a source later must not silently delete history,
it must just stop that history from being usable. Permission is therefore
enforced only at retrieval time, by reusing the same permissions service
that gates POST /data (app/permissions/service.py) — there is exactly one
place in this codebase that knows whether a source is enabled.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.config import DEMO_USER_ID
from app.models.database import db_cursor
from app.models.schemas import Memory, MemoryCreate
from app.permissions.service import is_enabled


def create_memory(payload: MemoryCreate) -> Memory:
    """Store a memory. id and timestamp are always generated here."""

    memory_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)

    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO memories (id, user_id, content, source, timestamp, importance) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (memory_id, DEMO_USER_ID, payload.content, payload.source, timestamp.isoformat(), payload.importance),
        )

    return Memory(
        id=memory_id,
        content=payload.content,
        source=payload.source,
        timestamp=timestamp,
        importance=payload.importance,
    )


def get_memories() -> list[Memory]:
    """Return stored memories whose source is CURRENTLY enabled.

    A memory whose source has since been disabled remains in the database
    (see module docstring) but is filtered out here, so it stops being
    usable the moment permission is revoked — no separate cleanup needed.
    Re-enabling the source makes it visible again on the very next call.
    """

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, content, source, timestamp, importance FROM memories "
            "WHERE user_id = ? ORDER BY timestamp DESC",
            (DEMO_USER_ID,),
        )
        rows = cur.fetchall()

    return [
        Memory(
            id=row["id"],
            content=row["content"],
            source=row["source"],
            timestamp=row["timestamp"],
            importance=row["importance"],
        )
        for row in rows
        if is_enabled(row["source"])
    ]


def delete_memory(memory_id: str) -> bool:
    """Delete one memory by id. Returns False if it didn't exist."""

    with db_cursor() as cur:
        cur.execute(
            "SELECT id FROM memories WHERE id = ? AND user_id = ?",
            (memory_id, DEMO_USER_ID),
        )
        if cur.fetchone() is None:
            return False
        cur.execute(
            "DELETE FROM memories WHERE id = ? AND user_id = ?",
            (memory_id, DEMO_USER_ID),
        )
    return True


def delete_all_memories() -> int:
    """Delete every stored memory for the demo user. Returns count removed."""

    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM memories WHERE user_id = ?", (DEMO_USER_ID,))
        count = cur.fetchone()["c"]
        cur.execute("DELETE FROM memories WHERE user_id = ?", (DEMO_USER_ID,))
    return count
