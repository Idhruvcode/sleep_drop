"""LangGraph application assembly."""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph
from pinecone import Pinecone

from sleep_assistant.config import load_environment, require_env
from sleep_assistant.graph.edges import configure_edges
from sleep_assistant.graph.nodes import (
    build_router_chain,
    build_sleep_chain,
    make_general_node,
    make_sleep_node,
    router_node,
)
from sleep_assistant.graph.state import ChatState
from sleep_assistant.services import build_chat_models, build_pinecone_index

logger = logging.getLogger(__name__)


def build_app():
    """Compile the LangGraph application."""

    load_environment()
    general_llm, sleep_llm, embedder = build_chat_models()
    pinecone_client = Pinecone(api_key=require_env("PINECONE_API_KEY"))
    index = build_pinecone_index(pinecone_client)

    router_chain = build_router_chain(general_llm)
    sleep_chain = build_sleep_chain(sleep_llm)

    graph = StateGraph(ChatState)

    def router_handler(state: ChatState) -> dict[str, object]:
        selected_route = router_node(state, router_chain)
        return {
            "route": selected_route,
            "current_route": selected_route,
            "last_node": "router",
        }

    graph.add_node("router", router_handler)
    graph.add_node("general", make_general_node(general_llm))
    graph.add_node("sleep", make_sleep_node(index, embedder, sleep_chain))

    configure_edges(graph)

    compiled = graph.compile()
    logger.info("LangGraph application compiled with nodes: %s", list(graph.nodes))
    return compiled


__all__ = ["build_app"]
