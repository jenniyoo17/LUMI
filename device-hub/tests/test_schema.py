import unittest
from datetime import datetime, timezone

from schemas.data_schema import StandardData, build_permission_denied_result


class StandardDataSchemaTests(unittest.TestCase):
    def test_standard_schema_serializes_iso_timestamp(self) -> None:
        timestamp = datetime(2026, 9, 26, 12, 30, tzinfo=timezone.utc)
        result = StandardData("notes", timestamp, True, {"text": "hello"})
        payload = result.to_dict()
        self.assertEqual(
            payload,
            {
                "source": "notes",
                "timestamp": "2026-09-26T12:30:00+00:00",
                "permission": True,
                "data": {"text": "hello"},
            },
        )

    def test_standard_schema_round_trips(self) -> None:
        payload = {
            "source": "calendar",
            "timestamp": "2026-09-27T10:00:00+00:00",
            "permission": True,
            "data": {"event": "DBMS Exam"},
        }
        self.assertEqual(StandardData.from_dict(payload).to_dict(), payload)

    def test_invalid_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            StandardData("email", datetime.now(timezone.utc), True, {})

    def test_naive_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            StandardData("notes", datetime(2026, 9, 26), True, {})

    def test_permission_must_be_boolean(self) -> None:
        with self.assertRaises(TypeError):
            StandardData("notes", datetime.now(timezone.utc), 1, {})  # type: ignore[arg-type]

    def test_data_must_be_a_mapping(self) -> None:
        with self.assertRaises(TypeError):
            StandardData("notes", datetime.now(timezone.utc), True, [])  # type: ignore[arg-type]

    def test_permission_denied_result_is_empty_and_standardized(self) -> None:
        result = build_permission_denied_result("health")
        self.assertEqual(set(result.to_dict()), {"source", "timestamp", "permission", "data"})
        self.assertFalse(result.permission)
        self.assertEqual(result.data, {})


if __name__ == "__main__":
    unittest.main()