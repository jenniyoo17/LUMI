"""Send authorized Device Hub notes to the Lumi backend."""

from __future__ import annotations

import json
from urllib import request

from schemas.data_schema import StandardData


def send_notes_to_lumi(
    data: StandardData,
    backend_url: str = "http://127.0.0.1:8000",
) -> dict[str, object]:
    """POST an authorized notes StandardData object to the existing /data API."""

    if data.source != "notes":
        raise ValueError("the Phase 4 bridge currently supports notes only")
    if not data.permission:
        raise PermissionError("Device Hub notes permission is disabled")

    body = json.dumps(data.to_dict()).encode("utf-8")
    req = request.Request(
        f"{backend_url.rstrip('/')}/data",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))