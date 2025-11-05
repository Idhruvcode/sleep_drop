"""Pydantic schemas and serialization helpers for the HTTP API."""

from __future__ import annotations

from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field


def message_to_dict(message: BaseMessage) -> Dict[str, str]:
    """Serialize LangChain message objects into role/content payloads."""

    role = "assistant"
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    else:
        role = getattr(message, "type", "assistant")

    return {"role": role, "content": message.content}


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    message: str = Field(..., min_length=1, description="User message to send to the bot")
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier to continue an existing conversation.",
    )


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""

    session_id: str
    reply: str
    route: str
    messages: List[Dict[str, str]]


__all__ = ["ChatRequest", "ChatResponse", "message_to_dict"]

