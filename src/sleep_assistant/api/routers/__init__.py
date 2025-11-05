"""API routers for the Sleep Assistant service."""

from __future__ import annotations

from .chat import router as chat_router

__all__ = ["chat_router"]

