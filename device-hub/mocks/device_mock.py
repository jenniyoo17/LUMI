"""Fictional generic device provider for the MVP."""

from typing import Any


class MockDeviceProvider:
    """Return clearly labeled fictional device status values."""

    def get_data(self) -> dict[str, Any]:
        return {
            "device_name": "Mock Smartwatch",
            "battery_percent": 78,
            "connected": True,
            "is_mock": True,
        }