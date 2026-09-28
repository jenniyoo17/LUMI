"""Retrieve relevant, currently authorized source data for chat context."""

from __future__ import annotations

import json
import re

from app.config import SUPPORTED_SOURCES
from app.models.database import db_cursor
from app.permissions.service import is_enabled


ContextCandidate = tuple[int, str, dict[str, str]]


def _sort_candidates(candidates: list[ContextCandidate]) -> None:
    candidates.sort(
        key=lambda candidate: (
            candidate[2]["sourceId"],
            candidate[2]["id"],
            candidate[2]["content"].casefold(),
        )
    )
    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]), reverse=True)


def _get_relevant_source_context(
    source: str,
    message: str,
    limit: int,
) -> list[ContextCandidate]:
    terms = set(re.findall(r"[a-z0-9]+", message.lower()))
    if not terms or limit <= 0:
        return []

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, timestamp, data FROM data_items "
            "WHERE source = ? AND permission = 1 ORDER BY timestamp DESC",
            (source,),
        )
        rows = cur.fetchall()

    ranked: list[ContextCandidate] = []
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
                    row["timestamp"],
                    {"id": row["id"], "content": text.strip(), "sourceId": source},
                )
            )

    _sort_candidates(ranked)
    return ranked[:limit]


def get_relevant_context(message: str, limit: int = 5) -> list[dict[str, str]]:
    """Retrieve currently authorized, relevant source context for a message.

    Notes and Calendar have retrieval contracts today. Other supported sources
    are permission-checked but contribute no context until implemented.
    """

    if limit <= 0:
        return []

    ranked_context: list[ContextCandidate] = []
    for source in sorted(SUPPORTED_SOURCES):
        if not is_enabled(source):
            continue
        if source in {"notes", "calendar"}:
            ranked_context.extend(_get_relevant_source_context(source, message, limit))
    _sort_candidates(ranked_context)
    return [context for _, _, context in ranked_context[:limit]]