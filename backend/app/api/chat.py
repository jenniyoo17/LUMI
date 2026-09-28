"""POST /chat — answer a user message using permission-enabled memories."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.chat.history_service import clear_history, get_history, save_exchange
from app.chat.service import MalformedLLMResponseError, chat
from app.llm.groq_service import LLMServiceError, MissingGroqAPIKeyError
from app.models.schemas import ChatHistoryClearResult, ChatHistoryMessage, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def send_message(payload: ChatRequest) -> ChatResponse:
    try:
        response = chat(payload.message)
    except MissingGroqAPIKeyError:
        raise HTTPException(status_code=503, detail="chat service is not configured") from None
    except LLMServiceError:
        raise HTTPException(status_code=502, detail="chat service request failed") from None
    except MalformedLLMResponseError:
        raise HTTPException(status_code=502, detail="chat service returned an invalid response") from None
    save_exchange(payload.message, response.response)
    return response


@router.get("/chat/history", response_model=list[ChatHistoryMessage])
def list_chat_history() -> list[ChatHistoryMessage]:
    return get_history()


@router.delete("/chat/history", response_model=ChatHistoryClearResult)
def delete_chat_history() -> ChatHistoryClearResult:
    return ChatHistoryClearResult(deleted_count=clear_history())