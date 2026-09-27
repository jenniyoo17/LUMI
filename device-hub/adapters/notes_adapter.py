"""Notes data adapter."""

from mocks.notes_mock import MockNotesProvider
from permissions.permission_manager import PermissionManager

from .base_adapter import BaseAdapter


class NotesAdapter(BaseAdapter):
    source = "notes"

    def __init__(
        self,
        permission_manager: PermissionManager,
        provider: MockNotesProvider | None = None,
    ) -> None:
        super().__init__(permission_manager, provider or MockNotesProvider())

    def __repr__(self) -> str:
        return "NotesAdapter(source='notes')"