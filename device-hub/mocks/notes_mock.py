"""Fictional notes provider for the MVP."""

from typing import Any


class MockNotesProvider:
    """Return a deterministic note; this is not connected to a notes service."""

    def get_data(self) -> dict[str, Any]:
        return {
            "text": "Normalization is an important DBMS topic.",
            "is_mock": True,
        }