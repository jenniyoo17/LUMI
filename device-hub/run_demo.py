"""Demonstrate that disabled sources cannot expose their mock data."""

from adapters.calendar_adapter import CalendarAdapter
from adapters.device_adapter import DeviceAdapter
from adapters.health_adapter import HealthAdapter
from adapters.notes_adapter import NotesAdapter
from permissions.permission_manager import PermissionManager


def main() -> None:
    permissions = PermissionManager()

    # Explicit user choices for this demonstration.
    permissions.enable("notes")
    permissions.enable("calendar")
    permissions.disable("health")
    permissions.disable("device")

    adapters = [
        ("Notes", NotesAdapter(permissions)),
        ("Calendar", CalendarAdapter(permissions)),
        ("Health", HealthAdapter(permissions)),
        ("Device", DeviceAdapter(permissions)),
    ]

    print("Permission state:")
    for source, enabled in permissions.get_permissions().items():
        print(f"  {source}: {'ON' if enabled else 'OFF'}")

    print("\nAdapter results:")
    for label, adapter in adapters:
        print(f"{label}: {adapter.fetch().to_dict()}")


if __name__ == "__main__":
    main()