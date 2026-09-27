"""POST /data — receives authorized (or denied) personal data items."""

from __future__ import annotations

from fastapi import APIRouter

from app.context.ingestion import store_incoming_data
from app.models.schemas import DataIngestResult, IncomingData

router = APIRouter()


@router.post("/data", response_model=DataIngestResult)
def receive_data(item: IncomingData) -> DataIngestResult:
    """Accepts device-hub's StandardData.to_dict() shape directly.

    {
      "source": "notes | calendar | health | device | messages",
      "timestamp": "ISO-8601",
      "permission": true,
      "data": {}
    }
    """

    return store_incoming_data(item)
