"""Retrieve relevant, currently authorized source data for chat context."""

from __future__ import annotations

import json
import re

from app.config import SUPPORTED_SOURCES
from app.models.database import db_cursor
from app.permissions.service import is_enabled


def _get_relevant_source_context(
    source: str,
    message: str,
    limit: int,
) -> list[tuple[int, dict[str, str]]]:
    terms = set(re.findall(r"[a-z0-9]+", message.lower()))
    if not terms or limit <= 0:
        return []

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, data FROM data_items "
            "WHERE source = ? AND permission = 1 ORDER BY timestamp DESC",
            (source,),
        )
        rows = cur.fetchall()

    ranked: list[tuple[int, dict[str, str]]] = []
    for row in rows:
        payload = json.loads(row["data"])
        if source == "notes":
            text = payload.get("text")
        elif source == "calendar":
            event = payload.get("event")
            event_time = payload.get("time")
            parts = [
                value.strip()
                for value in (event, event_time)
                if isinstance(value, str) and value.strip()
            ]
            text = " at ".join(parts)
        else:
            continue
        if not isinstance(text, str) or not text.strip():
            continue
        overlap = terms & set(re.findall(r"[a-z0-9]+", text.lower()))
        if overlap:
            ranked.append(
                (
                    len(overlap),
                    {"id": row["id"], "content": text.strip(), "sourceId": source},
                )
            )

    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:limit]


def get_relevant_context(message: str, limit: int = 5) -> list[dict[str, str]]:
    """Retrieve currently authorized, relevant source context for a message.

    Notes and Calendar have retrieval contracts today. Other supported sources
    are permission-checked but contribute no context until implemented.
    """

    if limit <= 0:
        return []

    ranked_context: list[tuple[int, dict[str, str]]] = []
    for source in sorted(SUPPORTED_SOURCES):
        if not is_enabled(source):
            continue
        if source in {"notes", "calendar"}:
            ranked_context.extend(_get_relevant_source_context(source, message, limit))
    ranked_context.sort(key=lambda item: item[0], reverse=True)
    return [context for _, context in ranked_context[:limit]]