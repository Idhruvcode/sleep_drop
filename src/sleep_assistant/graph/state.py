"""Shared types and helpers for LangGraph state management."""

from __future__ import annotations

from typing import Annotated, List, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import add_messages

MAX_USER_HISTORY = 5


def _append_user_history(existing: List[str] | None, new_entries: List[str] | None) -> List[str]:
    """Merge user-history entries while enforcing the history window."""

    history = list(existing or [])
    if new_entries:
        history.extend(entry for entry in new_entries if entry)
        if len(history) > MAX_USER_HISTORY:
            history = history[-MAX_USER_HISTORY:]
    return history


class ChatState(TypedDict, total=False):
    """Shared conversation state for the LangGraph agent."""

    messages: Annotated[List[BaseMessage], add_messages]
    user_history: Annotated[List[str], _append_user_history]
    route: Literal["general", "sleep"]
    current_route: str
    last_node: str
    retrievals: List["RetrievedDocument"]


class RetrievedDocument(TypedDict, total=False):
    """Metadata captured from the vector store for transparency."""

    text: str
    page_number: int | str
    source_document: str
    score: float


def record_user_message(state: "ChatState", content: str, *, max_history: int = MAX_USER_HISTORY) -> None:
    """Append a human message to the state and maintain a small user-history window."""

    normalized = content.strip()
    if not normalized:
        return

    messages = state.setdefault("messages", [])
    messages.append(HumanMessage(content=normalized))

    history = state.setdefault("user_history", [])
    history.append(normalized)
    if len(history) > max_history:
        del history[: len(history) - max_history]


def get_recent_user_messages(state: "ChatState", limit: int | None = None) -> List[str]:
    """Return the most recent user messages, falling back to message objects if needed."""

    history = list(state.get("user_history") or [])
    if not history:
        collected: List[str] = []
        for message in reversed(state.get("messages", [])):
            if isinstance(message, HumanMessage):
                # Convert content to string - it may be str, list, or dict
                content = message.content
                content_str = content if isinstance(content, str) else str(content)
                collected.append(content_str)
                if limit and len(collected) >= limit:
                    break
        history = list(reversed(collected))

    if not limit:
        limit = MAX_USER_HISTORY
    return history[-limit:]


def get_last_user_message(state: "ChatState") -> str | None:
    """Return the latest user utterance, if present."""

    history = state.get("user_history")
    if history:
        return history[-1]

    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage):
            # Convert content to string - it may be str, list, or dict
            content = message.content
            return content if isinstance(content, str) else str(content)
    return None


__all__ = [
    "ChatState",
    "MAX_USER_HISTORY",
    "RetrievedDocument",
    "get_last_user_message",
    "get_recent_user_messages",
    "record_user_message",
]
