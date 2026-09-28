"""Send authorized Device Hub data to the Lumi backend."""

from __future__ import annotations

import json
from urllib import request

from schemas.data_schema import StandardData


SUPPORTED_BRIDGE_SOURCES = frozenset({"notes", "calendar"})


def send_data_to_lumi(
    data: StandardData,
    backend_url: str = "http://127.0.0.1:8000",
) -> dict[str, object]:
    """POST authorized Notes or Calendar StandardData to the existing /data API."""

    if data.source not in SUPPORTED_BRIDGE_SOURCES:
        raise ValueError("the bridge supports notes and calendar sources only")
    if not data.permission:
        raise PermissionError(f"Device Hub {data.source} permission is disabled")

    body = json.dumps(data.to_dict()).encode("utf-8")
    req = request.Request(
        f"{backend_url.rstrip('/')}/data",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def send_notes_to_lumi(
    data: StandardData,
    backend_url: str = "http://127.0.0.1:8000",
) -> dict[str, object]:
    """Backward-compatible Notes-only wrapper for the generic bridge."""

    if data.source != "notes":
        raise ValueError("send_notes_to_lumi only accepts notes data")
    return send_data_to_lumi(data, backend_url)