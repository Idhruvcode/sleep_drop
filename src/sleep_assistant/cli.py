"""Command-line helpers for interacting with the Sleep Assistant."""

from __future__ import annotations

import logging
import sys
from typing import List, Optional

from langchain_core.messages import AIMessage, HumanMessage

from sleep_assistant.graph import build_app
from sleep_assistant.graph.state import ChatState

logger = logging.getLogger(__name__)


def run_cli(app=None) -> None:
    """Simple command-line interface to interact with the chatbot."""

    if app is None:
        app = build_app()

    print("Sleep Assistant ready! Type your message (or 'exit' to quit).")
    state: ChatState = {"messages": []}

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        state["messages"].append(HumanMessage(content=user_input))
        state = app.invoke(state)
        route = state.get("current_route") or state.get("route", "sleep")
        logger.info("Route used for latest turn: %s", route)

        ai_response = next(
            (message.content for message in reversed(state["messages"]) if isinstance(message, AIMessage)),
            "I'm not sure how to respond to that.",
        )
        print(f"Bot: {ai_response}")


def main(argv: Optional[List[str]] = None) -> int:
    """Entrypoint for CLI usage."""

    if argv:
        print("This script does not take positional arguments. Launching CLI...")
    run_cli()
    return 0


__all__ = ["main", "run_cli"]
