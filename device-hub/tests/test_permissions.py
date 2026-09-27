import unittest

from permissions.permission_manager import PermissionManager


class PermissionManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.permissions = PermissionManager()

    def test_permissions_default_to_disabled(self) -> None:
        self.assertEqual(
            self.permissions.get_permissions(),
            {
                "calendar": False,
                "device": False,
                "health": False,
                "notes": False,
            },
        )

    def test_enable_permission(self) -> None:
        self.permissions.enable("notes")
        self.assertTrue(self.permissions.is_enabled("notes"))
        self.assertTrue(self.permissions.check_permission("notes"))

    def test_disable_permission(self) -> None:
        self.permissions.enable("health")
        self.permissions.disable("health")
        self.assertFalse(self.permissions.is_enabled("health"))

    def test_permissions_are_independent(self) -> None:
        self.permissions.enable("notes")
        self.assertTrue(self.permissions.is_enabled("notes"))
        self.assertFalse(self.permissions.is_enabled("calendar"))

    def test_unknown_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.permissions.enable("email")


if __name__ == "__main__":
    unittest.main()