"""Shared types for LangGraph state management."""

from __future__ import annotations

from typing import Annotated, List, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ChatState(TypedDict, total=False):
    """Shared conversation state for the LangGraph agent."""

    messages: Annotated[List[BaseMessage], add_messages]
    route: Literal["general", "sleep"]
    current_route: str
    last_node: str


__all__ = ["ChatState"]
