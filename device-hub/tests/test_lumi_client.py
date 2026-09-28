"""Tests for the Device Hub HTTP bridge to Lumi."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from adapters.calendar_adapter import CalendarAdapter
from adapters.notes_adapter import NotesAdapter
from lumi_client import send_data_to_lumi, send_notes_to_lumi
from permissions.permission_manager import PermissionManager
from schemas.data_schema import StandardData


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class LumiClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.permissions = PermissionManager()

    def _assert_posts_standard_data(self, data: StandardData) -> None:
        backend_result = {"stored": True, "reason": "stored", "source": data.source, "id": "item-1"}
        with patch("lumi_client.request.urlopen", return_value=FakeResponse(backend_result)) as urlopen:
            result = send_data_to_lumi(data, "http://test.local/")

        self.assertEqual(result, backend_result)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://test.local/data")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data.decode("utf-8")), data.to_dict())

    def test_authorized_notes_can_still_be_sent_through_legacy_function(self) -> None:
        self.permissions.enable("notes")
        data = NotesAdapter(self.permissions).fetch()

        self._assert_posts_standard_data(data)
        with patch(
            "lumi_client.request.urlopen",
            return_value=FakeResponse({"stored": True, "source": "notes"}),
        ):
            self.assertEqual(send_notes_to_lumi(data)["source"], "notes")

    def test_authorized_calendar_can_be_sent(self) -> None:
        self.permissions.enable("calendar")
        data = CalendarAdapter(self.permissions).fetch()

        self.assertEqual(
            data.data,
            {
                "event": "DBMS Exam",
                "time": "2026-09-27T10:00:00",
                "is_mock": True,
            },
        )
        self._assert_posts_standard_data(data)

    def test_denied_calendar_raises_permission_error_without_http_request(self) -> None:
        data = CalendarAdapter(self.permissions).fetch()

        with patch("lumi_client.request.urlopen") as urlopen:
            with self.assertRaisesRegex(PermissionError, "calendar permission is disabled"):
                send_data_to_lumi(data)
        urlopen.assert_not_called()

    def test_unsupported_source_is_rejected(self) -> None:
        data = StandardData(
            source="health",
            timestamp=datetime.now(timezone.utc),
            permission=True,
            data={"heart_rate": 82},
        )

        with patch("lumi_client.request.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "notes and calendar"):
                send_data_to_lumi(data)
        urlopen.assert_not_called()

    def test_legacy_notes_function_rejects_calendar(self) -> None:
        self.permissions.enable("calendar")
        data = CalendarAdapter(self.permissions).fetch()

        with patch("lumi_client.request.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "only accepts notes"):
                send_notes_to_lumi(data)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()