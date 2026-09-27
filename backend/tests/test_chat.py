"""Phase 3 chat API tests; all model responses are mocked."""

from __future__ import annotations

import json

from app.permissions.service import set_permission


def _mock_model(monkeypatch, result, captured=None):
    def generate(messages):
        if captured is not None:
            captured.extend(messages)
        return result

    monkeypatch.setattr("app.chat.service.generate_response", generate)


def test_chat_returns_groq_response(client, monkeypatch):
    _mock_model(monkeypatch, '{"response":"You could start with your main priority.","used_memory_ids":[]}')

    response = client.post("/chat", json={"message": "What should I focus on today?"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "You could start with your main priority.",
        "used_context": [],
        "memory_ids": [],
    }


def test_chat_passes_relevant_enabled_memory_and_reports_only_used(client, monkeypatch):
    set_permission("notes", True)
    relevant = client.post(
        "/memory", json={"content": "My DBMS exam is tomorrow", "source": "notes"}
    ).json()
    client.post("/memory", json={"content": "Buy oat milk", "source": "notes"})
    captured = []
    _mock_model(
        monkeypatch,
        json.dumps({"response": "Let's review DBMS first.", "used_memory_ids": [relevant["id"]]}),
        captured,
    )

    response = client.post("/chat", json={"message": "How should I prepare for my DBMS exam?"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Let's review DBMS first."
    assert body["used_context"] == [{"label": "My DBMS exam is tomorrow", "sourceId": "notes"}]
    assert body["memory_ids"] == [relevant["id"]]
    supplied = json.loads(captured[1]["content"])["memories"]
    assert [memory["id"] for memory in supplied] == [relevant["id"]]


def test_disabled_source_memory_is_not_passed_to_model(client, monkeypatch):
    set_permission("health", True)
    memory = client.post(
        "/memory", json={"content": "I slept poorly before my exam", "source": "health"}
    ).json()
    set_permission("health", False)
    captured = []
    _mock_model(monkeypatch, '{"response":"I can help you plan.","used_memory_ids":[]}', captured)

    response = client.post("/chat", json={"message": "How can I prepare for my exam?"})

    assert response.status_code == 200
    assert memory["content"] not in str(captured)
    assert response.json()["used_context"] == []


def test_chat_rejects_empty_message(client, monkeypatch):
    _mock_model(monkeypatch, '{"response":"hello","used_memory_ids":[]}')

    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 422


def test_chat_handles_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr("app.chat.service.generate_response", __import__("app.llm.groq_service", fromlist=["generate_response"]).generate_response)

    response = client.post("/chat", json={"message": "Hi Lumi"})

    assert response.status_code == 503
    assert "GROQ_API_KEY" not in response.text


def test_chat_handles_groq_failure(client, monkeypatch):
    from app.llm.groq_service import LLMServiceError

    def fail(_messages):
        raise LLMServiceError("private sdk detail")

    monkeypatch.setattr("app.chat.service.generate_response", fail)

    response = client.post("/chat", json={"message": "Hi Lumi"})

    assert response.status_code == 502
    assert "private sdk detail" not in response.text


def test_chat_handles_malformed_model_response(client, monkeypatch):
    _mock_model(monkeypatch, "not json")

    response = client.post("/chat", json={"message": "Hi Lumi"})

    assert response.status_code == 502