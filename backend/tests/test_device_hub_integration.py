"""Integration coverage for Device Hub notes and Lumi /data + /chat."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

DEVICE_HUB_PATH = Path(__file__).resolve().parents[2] / "device-hub"
sys.path.insert(0, str(DEVICE_HUB_PATH))

from adapters.notes_adapter import NotesAdapter  # noqa: E402
from lumi_client import send_notes_to_lumi  # noqa: E402
from permissions.permission_manager import PermissionManager  # noqa: E402
from app.models.database import db_cursor  # noqa: E402
from app.permissions.service import set_permission  # noqa: E402


class DemoNotesProvider:
    def __init__(self, text: str = "My DBMS exam is tomorrow morning.") -> None:
        self.text = text
        self.calls = 0

    def get_data(self) -> dict[str, object]:
        self.calls += 1
        return {"text": self.text, "is_mock": True}


def _connect_bridge_to_test_client(monkeypatch, client):
    def fake_urlopen(req, timeout):
        assert timeout == 10
        response = client.post(
            req.full_url.removeprefix("http://testserver"),
            content=req.data,
            headers={"content-type": "application/json"},
        )
        return io.BytesIO(response.content)

    monkeypatch.setattr("lumi_client.request.urlopen", fake_urlopen)


def test_device_hub_notes_adapter_produces_standard_data():
    permissions = PermissionManager()
    permissions.enable("notes")
    data = NotesAdapter(permissions, DemoNotesProvider()).fetch().to_dict()

    assert set(data) == {"source", "timestamp", "permission", "data"}
    assert data["source"] == "notes"
    assert data["permission"] is True
    assert data["data"] == {
        "text": "My DBMS exam is tomorrow morning.",
        "is_mock": True,
    }


def test_authorized_notes_travel_through_data_and_into_chat(client, monkeypatch):
    set_permission("notes", True)
    _connect_bridge_to_test_client(monkeypatch, client)
    permissions = PermissionManager()
    permissions.enable("notes")
    data = NotesAdapter(permissions, DemoNotesProvider()).fetch()

    ingestion = send_notes_to_lumi(data)

    assert ingestion["stored"] is True
    assert ingestion["source"] == "notes"
    captured = {}

    def fake_model(messages):
        request_payload = json.loads(messages[1]["content"])
        captured.update(request_payload)
        used_data_ids = (
            [request_payload["notes_context"][0]["id"]]
            if request_payload["notes_context"]
            else []
        )
        return json.dumps(
            {
                "response": (
                    "Your DBMS exam is tomorrow morning."
                    if used_data_ids
                    else "I do not have that note available."
                ),
                "used_memory_ids": [],
                "used_data_ids": used_data_ids,
            }
        )

    monkeypatch.setattr("app.chat.service.generate_response", fake_model)
    response = client.post("/chat", json={"message": "When is my DBMS exam?"})

    assert response.status_code == 200
    assert captured["notes_context"][0]["content"] == "My DBMS exam is tomorrow morning."
    assert response.json()["response"] == "Your DBMS exam is tomorrow morning."
    assert response.json()["used_context"] == [
        {"label": "My DBMS exam is tomorrow morning.", "sourceId": "notes"}
    ]
    assert response.json()["memory_ids"] == []

    set_permission("notes", False)
    captured.clear()
    response = client.post("/chat", json={"message": "When is my DBMS exam?"})

    assert response.status_code == 200
    assert captured["notes_context"] == []
    assert response.json()["used_context"] == []


def test_backend_permission_disabled_does_not_store_or_use_notes(client, monkeypatch):
    _connect_bridge_to_test_client(monkeypatch, client)
    permissions = PermissionManager()
    permissions.enable("notes")
    data = NotesAdapter(permissions, DemoNotesProvider()).fetch()

    ingestion = send_notes_to_lumi(data)

    assert ingestion["stored"] is False
    with db_cursor() as cur:
        cur.execute("SELECT data, permission FROM data_items WHERE source = 'notes'")
        row = cur.fetchone()
    assert row["permission"] == 0
    assert row["data"] == "{}"
    captured = {}

    def fake_model(messages):
        captured.update(json.loads(messages[1]["content"]))
        return '{"response":"I do not have that note available.","used_memory_ids":[]}'

    monkeypatch.setattr("app.chat.service.generate_response", fake_model)
    response = client.post("/chat", json={"message": "When is my DBMS exam?"})

    assert response.status_code == 200
    assert captured["notes_context"] == []
    assert response.json()["used_context"] == []


def test_device_hub_permission_disabled_does_not_produce_or_send_notes(monkeypatch):
    provider = DemoNotesProvider()
    data = NotesAdapter(PermissionManager(), provider).fetch()
    urlopen_called = False

    def unexpected_urlopen(_request, timeout):
        nonlocal urlopen_called
        urlopen_called = True
        raise AssertionError("disabled Device Hub data must not be sent")

    monkeypatch.setattr("lumi_client.request.urlopen", unexpected_urlopen)

    assert data.permission is False
    assert data.data == {}
    assert provider.calls == 0
    with pytest.raises(PermissionError):
        send_notes_to_lumi(data)
    assert urlopen_called is False