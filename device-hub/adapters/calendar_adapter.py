"""Calendar data adapter."""

from mocks.calendar_mock import MockCalendarProvider
from permissions.permission_manager import PermissionManager

from .base_adapter import BaseAdapter


class CalendarAdapter(BaseAdapter):
    source = "calendar"

    def __init__(
        self,
        permission_manager: PermissionManager,
        provider: MockCalendarProvider | None = None,
    ) -> None:
        super().__init__(permission_manager, provider or MockCalendarProvider())

    def __repr__(self) -> str:
        return "CalendarAdapter(source='calendar')"