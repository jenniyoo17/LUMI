"""Groq-backed implementation of Lumi's language model interface."""

from __future__ import annotations

import os


class MissingGroqAPIKeyError(RuntimeError):
    """Raised when a model request is attempted without GROQ_API_KEY."""


class LLMServiceError(RuntimeError):
    """Raised when Groq fails or returns an unusable response."""


def generate_response(messages: list[dict[str, str]]) -> str:
    """Return the assistant message from Groq without exposing SDK details."""

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise MissingGroqAPIKeyError

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
            messages=messages,
        )
        content = completion.choices[0].message.content
    except MissingGroqAPIKeyError:
        raise
    except Exception as exc:
        raise LLMServiceError("Groq request failed") from exc

    if not isinstance(content, str) or not content.strip():
        raise LLMServiceError("Groq returned an empty response")
    return content