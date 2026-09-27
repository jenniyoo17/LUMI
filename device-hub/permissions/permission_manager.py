"""Centralized, privacy-first permissions for device hub data sources."""

from __future__ import annotations

from schemas.data_schema import SUPPORTED_SOURCES


class PermissionManager:
    """Track independent opt-in permissions for each supported source.

    All permissions start disabled. Adapters receive this manager and must
    check it before asking their provider for any source data.
    """

    def __init__(self) -> None:
        self._permissions = {source: False for source in sorted(SUPPORTED_SOURCES)}

    def _validate_source(self, source: str) -> None:
        if source not in SUPPORTED_SOURCES:
            supported = ", ".join(sorted(SUPPORTED_SOURCES))
            raise ValueError(f"source must be one of: {supported}")

    def enable(self, source: str) -> None:
        """Grant access to one source."""

        self._validate_source(source)
        self._permissions[source] = True

    def disable(self, source: str) -> None:
        """Revoke access to one source."""

        self._validate_source(source)
        self._permissions[source] = False

    def is_enabled(self, source: str) -> bool:
        """Return whether a source has been explicitly enabled."""

        self._validate_source(source)
        return self._permissions[source]

    def check_permission(self, source: str) -> bool:
        """Adapter-friendly permission check.

        This named method makes the privacy gate explicit at each adapter
        boundary while keeping the state in one manager.
        """

        return self.is_enabled(source)

    def get_permissions(self) -> dict[str, bool]:
        """Return a copy so callers cannot mutate manager state indirectly."""

        return self._permissions.copy()