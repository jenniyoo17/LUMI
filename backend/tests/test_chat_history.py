"""Tests for persistent conversation history, separate from personal memory."""

from __future__ import annotations

import json

from app.llm.groq_service import LLMServiceError


def _mock_model(monkeypatch, response):
    monkeypatch.setattr("app.chat.service.generate_response", lambda _messages: response)


def test_chat_history_is_initially_empty(client):
    response = client.get("/chat/history")

    assert response.status_code == 200
    assert response.json() == []


def test_successful_chat_saves_exchange_and_keeps_response_contract(client, monkeypatch):
    _mock_model(
        monkeypatch,
        json.dumps({"response": "Hi! How can I help?", "used_memory_ids": []}),
    )

    chat_response = client.post("/chat", json={"message": "Hello"})

    assert chat_response.status_code == 200
    assert chat_response.json() == {
        "response": "Hi! How can I help?",
        "used_context": [],
        "memory_ids": [],
    }
    history = client.get("/chat/history").json()
    assert len(history) == 2
    assert [message["role"] for message in history] == ["user", "assistant"]
    assert [message["content"] for message in history] == ["Hello", "Hi! How can I help?"]
    assert history[0]["id"]
    assert history[0]["timestamp"] < history[1]["timestamp"]
    assert client.get("/memory").json() == []


def test_multiple_chat_turns_are_chronological(client, monkeypatch):
    _mock_model(monkeypatch, '{"response":"A reply","used_memory_ids":[]}')

    client.post("/chat", json={"message": "First turn"})
    client.post("/chat", json={"message": "Second turn"})

    history = client.get("/chat/history").json()
    assert [message["content"] for message in history] == [
        "First turn",
        "A reply",
        "Second turn",
        "A reply",
    ]
    assert [message["role"] for message in history] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]


def test_delete_chat_history_clears_current_users_messages(client, monkeypatch):
    _mock_model(monkeypatch, '{"response":"A reply","used_memory_ids":[]}')
    client.post("/chat", json={"message": "Hello"})

    response = client.delete("/chat/history")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 2}
    assert client.get("/chat/history").json() == []


def test_groq_failure_does_not_save_messages(client, monkeypatch):
    def fail(_messages):
        raise LLMServiceError("request failed")

    monkeypatch.setattr("app.chat.service.generate_response", fail)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 502
    assert client.get("/chat/history").json() == []


def test_invalid_groq_response_does_not_save_messages(client, monkeypatch):
    _mock_model(monkeypatch, "not json")

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 502
    assert client.get("/chat/history").json() == []