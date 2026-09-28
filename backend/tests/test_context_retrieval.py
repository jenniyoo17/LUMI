"""Tests for the generic authorized personal-context retrieval interface."""

from __future__ import annotations

from app.context.retrieval import get_relevant_context
from app.models.database import db_cursor
from app.permissions.service import set_permission


def _ingest_note(client, text: str, timestamp: str) -> None:
    response = client.post(
        "/data",
        json={
            "source": "notes",
            "timestamp": timestamp,
            "permission": True,
            "data": {"text": text, "is_mock": True},
        },
    )
    assert response.status_code == 200
    assert response.json()["stored"] is True


def _ingest_calendar(client, event: str, event_time: str, timestamp: str) -> None:
    response = client.post(
        "/data",
        json={
            "source": "calendar",
            "timestamp": timestamp,
            "permission": True,
            "data": {"event": event, "time": event_time, "is_mock": True},
        },
    )
    assert response.status_code == 200
    assert response.json()["stored"] is True


def test_relevant_notes_are_returned_as_generic_context(client):
    set_permission("notes", True)
    _ingest_note(client, "My DBMS exam is tomorrow morning.", "2026-09-27T12:00:00+00:00")

    context = get_relevant_context("When is my DBMS exam?")

    assert len(context) == 1
    assert context[0]["content"] == "My DBMS exam is tomorrow morning."
    assert context[0]["sourceId"] == "notes"
    assert context[0]["id"]


def test_disabled_notes_permission_hides_previously_stored_context(client):
    set_permission("notes", True)
    _ingest_note(client, "My DBMS exam is tomorrow.", "2026-09-27T12:00:00+00:00")
    assert get_relevant_context("DBMS exam")

    set_permission("notes", False)

    assert get_relevant_context("DBMS exam") == []


def test_irrelevant_notes_are_not_returned(client):
    set_permission("notes", True)
    _ingest_note(client, "Buy apples and bread after work.", "2026-09-27T12:00:00+00:00")

    assert get_relevant_context("When is the DBMS exam?") == []


def test_context_limit_is_respected_in_relevance_order(client):
    set_permission("notes", True)
    _ingest_note(client, "DBMS exam notes from yesterday.", "2026-09-25T12:00:00+00:00")
    _ingest_note(client, "DBMS exam notes from today.", "2026-09-26T12:00:00+00:00")
    _ingest_note(client, "DBMS exam notes from this morning.", "2026-09-27T12:00:00+00:00")

    context = get_relevant_context("DBMS", limit=2)

    assert len(context) == 2
    assert [item["content"] for item in context] == [
        "DBMS exam notes from this morning.",
        "DBMS exam notes from today.",
    ]


def test_denied_data_item_payload_is_never_retrieved(client):
    set_permission("notes", True)
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO data_items (id, source, timestamp, permission, data) "
            "VALUES (?, 'notes', ?, 0, ?)",
            ("denied-notes", "2026-09-27T12:00:00+00:00", '{"text":"DBMS exam secret"}'),
        )

    assert get_relevant_context("DBMS exam") == []


def test_supported_non_notes_sources_do_not_produce_context(client):
    for source in ("calendar", "health", "device", "messages"):
        set_permission(source, True)
        response = client.post(
            "/data",
            json={
                "source": source,
                "timestamp": "2026-09-27T12:00:00+00:00",
                "permission": True,
                "data": {"unimplemented_payload": "DBMS exam tomorrow"},
            },
        )
        assert response.status_code == 200
        assert response.json()["stored"] is True

    assert get_relevant_context("DBMS exam tomorrow") == []


def test_non_positive_context_limit_returns_empty(client):
    set_permission("notes", True)
    _ingest_note(client, "DBMS exam tomorrow.", "2026-09-27T12:00:00+00:00")

    assert get_relevant_context("DBMS", limit=0) == []


def test_higher_scoring_calendar_ranks_above_newer_lower_scoring_note(client):
    set_permission("notes", True)
    set_permission("calendar", True)
    _ingest_note(client, "alpha only", "2026-09-27T15:00:00+00:00")
    _ingest_calendar(
        client,
        "alpha beta",
        "2026-09-27T10:00:00",
        "2026-09-27T12:00:00+00:00",
    )

    context = get_relevant_context("alpha beta")

    assert context[0]["sourceId"] == "calendar"
    assert context[0]["content"] == "alpha beta at 2026-09-27T10:00:00"


def test_higher_scoring_note_ranks_above_newer_lower_scoring_calendar(client):
    set_permission("notes", True)
    set_permission("calendar", True)
    _ingest_note(client, "alpha beta", "2026-09-27T10:00:00+00:00")
    _ingest_calendar(
        client,
        "alpha only",
        "2026-09-27T15:00:00",
        "2026-09-27T15:00:00+00:00",
    )

    context = get_relevant_context("alpha beta")

    assert context[0]["sourceId"] == "notes"
    assert context[0]["content"] == "alpha beta"


def test_equal_scores_use_timestamp_then_source_id_tie_breaker(client):
    set_permission("notes", True)
    set_permission("calendar", True)
    timestamp = "2026-09-27T12:00:00+00:00"
    _ingest_note(client, "alpha", timestamp)
    _ingest_calendar(client, "alpha", "", timestamp)

    first_result = get_relevant_context("alpha")
    second_result = get_relevant_context("alpha")

    assert first_result == second_result
    assert [item["sourceId"] for item in first_result] == ["calendar", "notes"]


def test_cross_source_results_never_exceed_five(client):
    set_permission("notes", True)
    set_permission("calendar", True)
    for index in range(3):
        _ingest_note(
            client,
            f"alpha note {index}",
            f"2026-09-27T1{index}:00:00+00:00",
        )
        _ingest_calendar(
            client,
            f"alpha event {index}",
            "",
            f"2026-09-27T0{index}:00:00+00:00",
        )

    assert len(get_relevant_context("alpha")) == 5


def test_relevant_calendar_event_returns_event_name_and_time_without_memory(client):
    set_permission("calendar", True)
    _ingest_calendar(
        client,
        "DBMS Exam",
        "2026-09-27T10:00:00",
        "2026-09-26T12:00:00+00:00",
    )

    context = get_relevant_context("When is my DBMS exam?")

    assert len(context) == 1
    assert context[0]["content"] == "DBMS Exam at 2026-09-27T10:00:00"
    assert context[0]["sourceId"] == "calendar"
    assert "is_mock" not in context[0]["content"]
    assert client.get("/memory").json() == []


def test_disabled_calendar_permission_hides_previously_stored_event(client):
    set_permission("calendar", True)
    _ingest_calendar(
        client,
        "DBMS Exam",
        "2026-09-27T10:00:00",
        "2026-09-26T12:00:00+00:00",
    )
    assert get_relevant_context("DBMS exam")

    set_permission("calendar", False)

    assert get_relevant_context("DBMS exam") == []


def test_calendar_relevance_selects_matching_event(client):
    set_permission("calendar", True)
    _ingest_calendar(
        client,
        "DBMS Exam",
        "2026-09-27T10:00:00",
        "2026-09-26T12:00:00+00:00",
    )
    _ingest_calendar(
        client,
        "Project Meeting",
        "2026-09-27T14:00:00",
        "2026-09-26T13:00:00+00:00",
    )

    context = get_relevant_context("When is the DBMS exam?")

    assert [item["content"] for item in context] == ["DBMS Exam at 2026-09-27T10:00:00"]


def test_chat_uses_calendar_context_and_reports_calendar_source(client, monkeypatch):
    import json

    set_permission("calendar", True)
    _ingest_calendar(
        client,
        "DBMS Exam",
        "2026-09-27T10:00:00",
        "2026-09-26T12:00:00+00:00",
    )
    captured = {}

    def mock_model(messages):
        payload = json.loads(messages[1]["content"])
        captured.update(payload)
        calendar_id = payload["notes_context"][0]["id"]
        return json.dumps(
            {
                "response": "Your DBMS exam is at 10:00.",
                "used_memory_ids": [],
                "used_data_ids": [calendar_id, "unsupplied-calendar-id"],
            }
        )

    monkeypatch.setattr("app.chat.service.generate_response", mock_model)

    response = client.post("/chat", json={"message": "When is my DBMS exam?"})

    assert response.status_code == 200
    assert captured["notes_context"][0]["sourceId"] == "calendar"
    assert captured["notes_context"][0]["content"] == "DBMS Exam at 2026-09-27T10:00:00"
    assert response.json()["used_context"] == [
        {"label": "DBMS Exam at 2026-09-27T10:00:00", "sourceId": "calendar"}
    ]
    assert client.get("/memory").json() == []