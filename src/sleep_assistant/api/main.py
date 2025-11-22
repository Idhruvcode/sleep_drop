"""FastAPI application exposing the LangGraph chatbot."""

from __future__ import annotations

from fastapi import FastAPI

from sleep_assistant.api.deps import get_graph_app
from sleep_assistant.api.routers import chat_router
from sleep_assistant.config import load_environment
from sleep_assistant.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    load_environment()
    configure_logging()

    app = FastAPI(title="Sleep Assistant API", version="1.0.0")
    app.include_router(chat_router)

    @app.on_event("startup")
    async def _warm_graph() -> None:
        """Warm the LangGraph application so first requests are fast."""

        get_graph_app()

    return app


app = create_app()

__all__ = ["app", "create_app"]
