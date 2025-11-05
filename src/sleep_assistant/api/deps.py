"""Dependency helpers for the FastAPI layer."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict

from sleep_assistant.graph import build_app
from sleep_assistant.graph.state import ChatState

Sessions = Dict[str, ChatState]

_SESSIONS: Sessions = {}


@lru_cache(maxsize=1)
def get_graph_app():
    """Return a compiled LangGraph application."""

    return build_app()


def get_sessions_store() -> Sessions:
    """Return the in-memory session storage."""

    return _SESSIONS


__all__ = ["Sessions", "get_graph_app", "get_sessions_store"]
