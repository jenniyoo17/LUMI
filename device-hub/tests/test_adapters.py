import unittest

from adapters.calendar_adapter import CalendarAdapter
from adapters.device_adapter import DeviceAdapter
from adapters.health_adapter import HealthAdapter
from adapters.notes_adapter import NotesAdapter
from permissions.permission_manager import PermissionManager


class RecordingProvider:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.calls = 0

    def get_data(self) -> dict:
        self.calls += 1
        return self.data


class AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.permissions = PermissionManager()

    def test_notes_adapter_with_permission_enabled(self) -> None:
        self.permissions.enable("notes")
        result = NotesAdapter(self.permissions).fetch()
        self.assertEqual(result.source, "notes")
        self.assertTrue(result.permission)
        self.assertEqual(result.data["text"], "Normalization is an important DBMS topic.")

    def test_calendar_adapter_with_permission_enabled(self) -> None:
        self.permissions.enable("calendar")
        result = CalendarAdapter(self.permissions).get_data()
        self.assertEqual(result.source, "calendar")
        self.assertTrue(result.permission)
        self.assertEqual(result.data["event"], "DBMS Exam")

    def test_health_adapter_with_permission_enabled(self) -> None:
        self.permissions.enable("health")
        result = HealthAdapter(self.permissions).fetch()
        self.assertEqual(result.source, "health")
        self.assertTrue(result.permission)
        self.assertEqual(result.data["heart_rate"], 82)
        self.assertTrue(result.data["is_mock"])

    def test_health_adapter_with_permission_disabled(self) -> None:
        result = HealthAdapter(self.permissions).fetch()
        self.assertEqual(result.source, "health")
        self.assertFalse(result.permission)
        self.assertEqual(result.data, {})
        self.assertNotIn("heart_rate", result.data)

    def test_device_adapter_with_permission_enabled(self) -> None:
        self.permissions.enable("device")
        result = DeviceAdapter(self.permissions).fetch()
        self.assertEqual(result.source, "device")
        self.assertTrue(result.permission)
        self.assertEqual(result.data["device_name"], "Mock Smartwatch")

    def test_disabled_adapter_never_calls_provider(self) -> None:
        provider = RecordingProvider({"heart_rate": 999, "is_mock": True})
        result = HealthAdapter(self.permissions, provider=provider).fetch()
        self.assertFalse(result.permission)
        self.assertEqual(result.data, {})
        self.assertEqual(provider.calls, 0)

    def test_all_enabled_adapters_return_permission_true(self) -> None:
        adapters = [
            ("notes", NotesAdapter(self.permissions)),
            ("calendar", CalendarAdapter(self.permissions)),
            ("health", HealthAdapter(self.permissions)),
            ("device", DeviceAdapter(self.permissions)),
        ]
        for source, adapter in adapters:
            with self.subTest(source=source):
                self.permissions.enable(source)
                self.assertTrue(adapter.fetch().permission)


if __name__ == "__main__":
    unittest.main()