"""FastAPI application exposing the LangGraph chatbot."""

from __future__ import annotations

from fastapi import FastAPI

from sleep_assistant.api.routers import chat_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="Sleep Assistant API", version="1.0.0")
    app.include_router(chat_router)
    return app


app = create_app()

__all__ = ["app", "create_app"]

