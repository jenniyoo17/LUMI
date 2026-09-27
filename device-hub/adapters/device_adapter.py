"""Generic device data adapter."""

from mocks.device_mock import MockDeviceProvider
from permissions.permission_manager import PermissionManager

from .base_adapter import BaseAdapter


class DeviceAdapter(BaseAdapter):
    source = "device"

    def __init__(
        self,
        permission_manager: PermissionManager,
        provider: MockDeviceProvider | None = None,
    ) -> None:
        super().__init__(permission_manager, provider or MockDeviceProvider())

    def __repr__(self) -> str:
        return "DeviceAdapter(source='device')"