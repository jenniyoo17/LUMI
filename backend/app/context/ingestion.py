"""Ingest incoming personal data (POST /data).

Permission is enforced twice in this backend, deliberately:

1. HERE, at write time: if the incoming item says permission=false, its
   `data` payload is never persisted — only an empty audit row is kept,
   mirroring device-hub's own build_permission_denied_result() shape.
2. AGAIN, at read/use time (see app/context/retrieval.py): even a
   previously-stored, previously-authorized item is excluded from AI
   context if the source's CURRENT permission state is disabled. This
   means revoking a permission in Settings takes effect immediately for
   future conversations, without needing to delete old data.
"""

from __future__ import annotations

import json
import uuid

from app.models.database import db_cursor
from app.models.schemas import DataIngestResult, IncomingData


def store_incoming_data(item: IncomingData) -> DataIngestResult:
    item_id = str(uuid.uuid4())

    if not item.permission:
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
            reason="permission denied by data item; not stored or used",
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
