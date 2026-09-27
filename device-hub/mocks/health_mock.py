"""Fictional health/wearable provider for the MVP."""

from typing import Any


class MockHealthProvider:
    """Return clearly labeled fictional wearable values.

    These values are mock data only and do not come from a real health device.
    """

    def get_data(self) -> dict[str, Any]:
        return {
            "heart_rate": 82,
            "steps": 4300,
            "sleep_hours": 7.2,
            "is_mock": True,
        }