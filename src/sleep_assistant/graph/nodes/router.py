"""Routing helpers for the LangGraph chatbot."""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from sleep_assistant.graph.state import ChatState
from sleep_assistant.graph.prompts.router import get_router_prompt

logger = logging.getLogger(__name__)


def build_router_chain(router_llm: ChatOpenAI):
    """Return an LLM chain that classifies user inputs."""

    router_prompt = get_router_prompt()
    return router_prompt | router_llm


def router_node(state: ChatState, router_chain) -> str:
    """Choose between the general and sleep branches."""

    latest_user = next(
        (message.content for message in reversed(state["messages"]) if isinstance(message, HumanMessage)),
        None,
    )
    if not latest_user:
        return "sleep"

    judgment = router_chain.invoke({"question": latest_user}).content.strip().lower()
    route = "general" if "general" in judgment else "sleep"
    logger.info("Router selected '%s' node for message: %s", route, latest_user)
    return route
