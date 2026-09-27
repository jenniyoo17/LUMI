"""Shared adapter behavior and privacy enforcement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol

from permissions.permission_manager import PermissionManager
from schemas.data_schema import StandardData, build_permission_denied_result


class DataProvider(Protocol):
    """Minimal provider contract, allowing mocks to be replaced later."""

    def get_data(self) -> Mapping[str, Any]:
        ...


class BaseAdapter(ABC):
    """Template for permission-aware source adapters."""

    source: str

    def __init__(
        self,
        permission_manager: PermissionManager,
        provider: DataProvider,
    ) -> None:
        self.permission_manager = permission_manager
        self.provider = provider

    def fetch(self) -> StandardData:
        """Retrieve source data only after a successful permission check."""

        if not self.permission_manager.check_permission(self.source):
            return build_permission_denied_result(self.source)

        # The provider is intentionally called only inside the enabled branch.
        # This prevents a disabled adapter from even obtaining source data.
        data = self.provider.get_data()
        if not isinstance(data, Mapping):
            raise TypeError("data provider must return a mapping")

        return StandardData(
            source=self.source,
            timestamp=datetime.now(timezone.utc),
            permission=True,
            data=dict(data),
        )

    def get_data(self) -> StandardData:
        """Alias for callers that prefer a retrieval-oriented method name."""

        return self.fetch()

    @abstractmethod
    def __repr__(self) -> str:
        """Require concrete adapters to identify themselves for debugging."""

        raise NotImplementedError