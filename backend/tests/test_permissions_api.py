"""Tests for the HTTP API backed by Lumi's existing permission service."""

from __future__ import annotations

from app.permissions.service import get_all_permissions, is_enabled


def test_get_permissions_returns_all_supported_sources(client):
    response = client.get("/permissions")

    assert response.status_code == 200
    assert response.json() == {
        "calendar": False,
        "device": False,
        "health": False,
        "messages": False,
        "notes": False,
    }


def test_put_permissions_enables_source_through_existing_service(client):
    response = client.put("/permissions/notes", json={"enabled": True})

    assert response.status_code == 200
    assert response.json() == {"source": "notes", "enabled": True}
    assert is_enabled("notes") is True
    assert next(state.permission for state in get_all_permissions() if state.source == "notes") is True


def test_put_permissions_disables_source_through_existing_service(client):
    client.put("/permissions/notes", json={"enabled": True})

    response = client.put("/permissions/notes", json={"enabled": False})

    assert response.status_code == 200
    assert response.json() == {"source": "notes", "enabled": False}
    assert is_enabled("notes") is False


def test_put_permissions_rejects_unknown_source(client):
    response = client.put("/permissions/email", json={"enabled": True})

    assert response.status_code == 400
    assert "source must be one of" in response.json()["detail"]