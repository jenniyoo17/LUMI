"""Ingest incoming personal data (POST /data).

Permission is enforced at both boundaries and again at use time:

1. HERE, at write time: both the incoming Device Hub permission flag and
    the backend's independent current permission must be enabled. Otherwise
    the payload is discarded and only an empty audit row is retained.
2. At read/use time (see app/context/retrieval.py): previously stored data
    is excluded from AI context whenever the backend's current permission
    is disabled, so revocation immediately affects future conversations.
"""

from __future__ import annotations

import json
import uuid

from app.models.database import db_cursor
from app.models.schemas import DataIngestResult, IncomingData
from app.permissions.service import is_enabled


def store_incoming_data(item: IncomingData) -> DataIngestResult:
    item_id = str(uuid.uuid4())

    if not item.permission or not is_enabled(item.source):
        reason = (
            "permission denied by data item; not stored or used"
            if not item.permission
            else "backend permission disabled; not stored or used"
        )
        # Never persist the actual content of a denied item. Keep a bare
        # audit trail only, same spirit as device-hub's denied result.
        with db_cursor() as cur:
            cur.execute(
                "INSERT INTO data_items (id, source, timestamp, permission, data) "
                "VALUES (?, ?, ?, 0, '{}')",
                (item_id, item.source, item.timestamp.isoformat()),
            )
        return DataIngestResult(
            stored=False,
            reason=reason,
            source=item.source,
            id=item_id,
        )

    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO data_items (id, source, timestamp, permission, data) "
            "VALUES (?, ?, ?, 1, ?)",
            (item_id, item.source, item.timestamp.isoformat(), json.dumps(item.data)),
        )

    return DataIngestResult(stored=True, reason="stored", source=item.source, id=item_id)
