"""General-purpose LangGraph node definition."""

from __future__ import annotations

import logging
from typing import Dict

from langchain_openai import ChatOpenAI

from sleep_assistant.graph.state import ChatState

logger = logging.getLogger(__name__)


def make_general_node(general_llm: ChatOpenAI):
    """Return a LangGraph node callable for general chit-chat."""

    def node(state: ChatState) -> Dict[str, object]:
        logger.info("General node responding to latest message.")
        messages = state.get("messages", [])
        return {
            "messages": [general_llm.invoke(messages)],
            "route": "general",
            "current_route": "general",
            "last_node": "general",
            "retrievals": [],
        }

    return node
