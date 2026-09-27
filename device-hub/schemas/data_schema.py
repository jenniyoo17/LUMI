"""Validation and serialization for the device hub's standard data format."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class DataSource(str, Enum):
    """Data sources supported by the MVP."""

    NOTES = "notes"
    CALENDAR = "calendar"
    HEALTH = "health"
    DEVICE = "device"


SUPPORTED_SOURCES = frozenset(source.value for source in DataSource)


def _validate_source(source: str) -> str:
    if not isinstance(source, str) or source not in SUPPORTED_SOURCES:
        supported = ", ".join(sorted(SUPPORTED_SOURCES))
        raise ValueError(f"source must be one of: {supported}")
    return source


def _validate_timestamp(timestamp: datetime) -> datetime:
    if not isinstance(timestamp, datetime):
        raise TypeError("timestamp must be a datetime")
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset")
    return timestamp


@dataclass(frozen=True)
class StandardData:
    """A validated, serializable response from any data source.

    The ``data`` mapping is intentionally source-specific. Consumers can rely
    on the surrounding fields without knowing which adapter produced it.
    """

    source: str
    timestamp: datetime
    permission: bool
    data: Mapping[str, Any]

    def __post_init__(self) -> None:
        _validate_source(self.source)
        _validate_timestamp(self.timestamp)
        if not isinstance(self.permission, bool):
            raise TypeError("permission must be a boolean")
        if not isinstance(self.data, Mapping):
            raise TypeError("data must be a mapping")

    def to_dict(self) -> dict[str, Any]:
        """Return the public standard format with an ISO-8601 timestamp."""

        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "permission": self.permission,
            "data": dict(self.data),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "StandardData":
        """Validate and construct a response from a serialized payload."""

        if not isinstance(payload, Mapping):
            raise TypeError("standard data payload must be a mapping")

        required = {"source", "timestamp", "permission", "data"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"missing required fields: {', '.join(sorted(missing))}")

        timestamp = payload["timestamp"]
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError as exc:
                raise ValueError("timestamp must be a valid ISO-8601 value") from exc

        return cls(
            source=payload["source"],
            timestamp=timestamp,
            permission=payload["permission"],
            data=payload["data"],
        )


def build_permission_denied_result(source: str) -> StandardData:
    """Build a safe empty response without exposing disabled source data."""

    _validate_source(source)
    return StandardData(
        source=source,
        timestamp=datetime.now(timezone.utc),
        permission=False,
        data={},
    )