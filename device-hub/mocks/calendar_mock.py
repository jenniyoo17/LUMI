"""Fictional calendar provider for the MVP."""

from typing import Any


class MockCalendarProvider:
    """Return a deterministic calendar event; no calendar is connected."""

    def get_data(self) -> dict[str, Any]:
        return {
            "event": "DBMS Exam",
            "time": "2026-09-27T10:00:00",
            "is_mock": True,
        }