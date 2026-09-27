"""Tests for the Phase 2 memory service and API.

Permissions are toggled directly through app.permissions.service, the same
service the memory retrieval code itself calls — there's no HTTP endpoint
for permissions yet (that's Phase 1 spec, not built), so this is the
correct, real interface to drive from tests.
"""

from __future__ import annotations

from app.permissions.service import set_permission


def test_create_memory(client):
    set_permission("notes", True)

    response = client.post(
        "/memory",
        json={"content": "Exam tomorrow morning", "source": "notes", "importance": 0.8},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Exam tomorrow morning"
    assert body["source"] == "notes"
    assert body["importance"] == 0.8
    # id and timestamp are backend-generated, never client-supplied
    assert body["id"]
    assert body["timestamp"]


def test_retrieve_memory(client):
    set_permission("calendar", True)
    client.post("/memory", json={"content": "DBMS exam at 10am", "source": "calendar"})

    response = client.get("/memory")

    assert response.status_code == 200
    memories = response.json()
    assert len(memories) == 1
    assert memories[0]["content"] == "DBMS exam at 10am"


def test_delete_memory(client):
    set_permission("notes", True)
    created = client.post("/memory", json={"content": "temp note", "source": "notes"}).json()
    memory_id = created["id"]

    delete_response = client.delete(f"/memory/{memory_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True, "id": memory_id}

    get_response = client.get("/memory")
    assert get_response.json() == []


def test_delete_nonexistent_memory_returns_404(client):
    response = client.delete("/memory/does-not-exist")
    assert response.status_code == 404


def test_clear_all_memories(client):
    set_permission("notes", True)
    set_permission("calendar", True)
    client.post("/memory", json={"content": "a", "source": "notes"})
    client.post("/memory", json={"content": "b", "source": "calendar"})

    response = client.delete("/memory")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 2}
    assert client.get("/memory").json() == []


def test_disabled_source_excludes_memory(client):
    set_permission("health", True)
    client.post("/memory", json={"content": "slept 7 hours", "source": "health"})
    assert len(client.get("/memory").json()) == 1

    # Revoke permission after the memory was already stored.
    set_permission("health", False)

    response = client.get("/memory")
    assert response.status_code == 200
    assert response.json() == []  # excluded, but NOT deleted (see next test)


def test_reenabled_source_makes_memory_retrievable_again(client):
    set_permission("notes", True)
    created = client.post(
        "/memory", json={"content": "normalization notes", "source": "notes"}
    ).json()

    set_permission("notes", False)
    assert client.get("/memory").json() == []  # hidden while disabled

    set_permission("notes", True)
    memories_after_reenable = client.get("/memory").json()

    assert len(memories_after_reenable) == 1
    assert memories_after_reenable[0]["id"] == created["id"]
    assert memories_after_reenable[0]["content"] == "normalization notes"
