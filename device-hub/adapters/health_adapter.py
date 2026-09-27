"""Health/wearable data adapter using fictional values for the MVP."""

from mocks.health_mock import MockHealthProvider
from permissions.permission_manager import PermissionManager

from .base_adapter import BaseAdapter


class HealthAdapter(BaseAdapter):
    source = "health"

    def __init__(
        self,
        permission_manager: PermissionManager,
        provider: MockHealthProvider | None = None,
    ) -> None:
        super().__init__(permission_manager, provider or MockHealthProvider())

    def __repr__(self) -> str:
        return "HealthAdapter(source='health')"