"""Central permission checks. Every write or read of personal data goes
through here first — mirroring device-hub's PermissionManager philosophy
that a disabled source must never even be looked at, let alone used.
"""

from __future__ import annotations

from app.config import SUPPORTED_SOURCES
from app.models.database import db_cursor
from app.models.schemas import PermissionState


def is_enabled(source: str) -> bool:
    with db_cursor() as cur:
        cur.execute("SELECT permission FROM permissions WHERE source = ?", (source,))
        row = cur.fetchone()
    return bool(row["permission"]) if row else False


def set_permission(source: str, enabled: bool) -> PermissionState:
    if source not in SUPPORTED_SOURCES:
        supported = ", ".join(sorted(SUPPORTED_SOURCES))
        raise ValueError(f"source must be one of: {supported}")
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO permissions (source, permission) VALUES (?, ?) "
            "ON CONFLICT(source) DO UPDATE SET permission = excluded.permission",
            (source, int(enabled)),
        )
    return PermissionState(source=source, permission=enabled)


def get_all_permissions() -> list[PermissionState]:
    with db_cursor() as cur:
        cur.execute("SELECT source, permission FROM permissions ORDER BY source")
        rows = cur.fetchall()
    return [PermissionState(source=r["source"], permission=bool(r["permission"])) for r in rows]
