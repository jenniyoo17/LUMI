"""Build privacy-filtered context and orchestrate a Lumi response."""

from __future__ import annotations

import json
import re
from app.llm.groq_service import generate_response
from app.memory.service import get_memories
from app.models.schemas import ChatResponse, Memory, UsedContext

MAX_CONTEXT_MEMORIES = 5
STOP_WORDS = frozenset(
    {"about", "after", "again", "could", "focus", "from", "have", "into", "just", "should", "that", "their", "them", "there", "these", "this", "today", "what", "when", "where", "which", "with", "would", "your"}
)
SYSTEM_PROMPT = """You are Lumi, a warm, natural, concise personal AI companion. The supplied memories belong to the user and are private. Use them only when relevant to the user's message. Do not invent personal facts or claim to know anything not present in the supplied context. Respect privacy and do not claim access to data that was not provided.

Return only a JSON object with exactly these fields: "response" (a conversational string) and "used_memory_ids" (an array of IDs for supplied memories that materially informed your response). Return an empty array if no supplied memory was used. Never include an ID that was not supplied."""


class MalformedLLMResponseError(RuntimeError):
    """Raised when the language model output does not follow the chat contract."""


def _terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if len(term) > 2 and term not in STOP_WORDS
    }


def _select_relevant_memories(message: str) -> list[Memory]:
    message_terms = _terms(message)
    if not message_terms:
        return []

    scored = []
    for memory in get_memories():
        overlap = message_terms & _terms(memory.content)
        if overlap:
            score = len(overlap) / len(message_terms) + memory.importance * 0.01
            scored.append((score, memory))

    scored.sort(key=lambda item: (item[0], item[1].timestamp), reverse=True)
    return [memory for _, memory in scored[:MAX_CONTEXT_MEMORIES]]


def chat(message: str) -> ChatResponse:
    memories = _select_relevant_memories(message)
    serialized_memories = [
        {"id": memory.id, "content": memory.content, "sourceId": memory.source}
        for memory in memories
    ]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {"message": message, "memories": serialized_memories},
                ensure_ascii=True,
            ),
        },
    ]

    raw_response = generate_response(messages)
    try:
        result = json.loads(raw_response)
        response_text = result["response"]
        used_ids = result["used_memory_ids"]
        if (
            not isinstance(response_text, str)
            or not response_text.strip()
            or not isinstance(used_ids, list)
            or any(not isinstance(memory_id, str) for memory_id in used_ids)
        ):
            raise ValueError("invalid chat fields")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise MalformedLLMResponseError from exc

    memories_by_id = {memory.id: memory for memory in memories}
    used_context = [
        UsedContext(label=memories_by_id[memory_id].content, sourceId=memories_by_id[memory_id].source)
        for memory_id in dict.fromkeys(used_ids)
        if memory_id in memories_by_id
    ]
    return ChatResponse(
        response=response_text.strip(),
        used_context=used_context,
        memory_ids=[context_id for context_id in dict.fromkeys(used_ids) if context_id in memories_by_id],
    )