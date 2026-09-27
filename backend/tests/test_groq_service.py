"""Tests for the isolated Groq adapter."""

from __future__ import annotations

from types import SimpleNamespace

from app.llm.groq_service import generate_response


def test_generate_response_uses_available_default_model(monkeypatch):
    captured = {}

    class FakeGroq:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create_completion)
            )

        @staticmethod
        def create_completion(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="hello"))]
            )

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.setattr("groq.Groq", FakeGroq)

    response = generate_response([{"role": "user", "content": "hello"}])

    assert response == "hello"
    assert captured["model"] == "qwen/qwen3.8-27b"
    assert "response_format" not in captured