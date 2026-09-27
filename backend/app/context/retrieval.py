"""Retrieve relevant, currently authorized source data for chat context."""

from __future__ import annotations

import json
import re

from app.models.database import db_cursor
from app.permissions.service import is_enabled


def get_relevant_notes(message: str, limit: int = 5) -> list[dict[str, str]]:
    """Return relevant notes from authorized data items without making memories."""

    terms = set(re.findall(r"[a-z0-9]+", message.lower()))
    if not terms or limit <= 0 or not is_enabled("notes"):
        return []

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, data FROM data_items "
            "WHERE source = 'notes' AND permission = 1 ORDER BY timestamp DESC"
        )
        rows = cur.fetchall()

    ranked: list[tuple[int, dict[str, str]]] = []
    for row in rows:
        payload = json.loads(row["data"])
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        overlap = terms & set(re.findall(r"[a-z0-9]+", text.lower()))
        if overlap:
            ranked.append(
                (
                    len(overlap),
                    {"id": row["id"], "content": text.strip(), "sourceId": "notes"},
                )
            )

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [context for _, context in ranked[:limit]]