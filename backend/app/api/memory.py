"""POST/GET /memory, DELETE /memory/{id}, DELETE /memory.

Kept intentionally simple per Phase 2 scope: no embeddings, no relevance
ranking — just permission-aware CRUD. Retrieval logic lives in
app/memory/service.py, which is the only place that decides what "usable
memory" means.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.memory.service import create_memory, delete_all_memories, delete_memory, get_memories
from app.models.schemas import Memory, MemoryClearResult, MemoryCreate, MemoryDeleteResult

router = APIRouter()


@router.post("/memory", response_model=Memory)
def add_memory(payload: MemoryCreate) -> Memory:
    return create_memory(payload)


@router.get("/memory", response_model=list[Memory])
def list_memories() -> list[Memory]:
    """Returns only memories whose source is currently permission-enabled."""

    return get_memories()


@router.delete("/memory/{memory_id}", response_model=MemoryDeleteResult)
def remove_memory(memory_id: str) -> MemoryDeleteResult:
    deleted = delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="memory not found")
    return MemoryDeleteResult(deleted=True, id=memory_id)


@router.delete("/memory", response_model=MemoryClearResult)
def clear_memories() -> MemoryClearResult:
    """Deletes every stored memory, regardless of current permission state.

    This mirrors the frontend's clearAllMemories() intent: an explicit,
    total wipe the user asked for — not a permission-filtered view.
    """

    count = delete_all_memories()
    return MemoryClearResult(deleted_count=count)
