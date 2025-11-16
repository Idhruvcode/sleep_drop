"""Command-line helpers for interacting with the Sleep Assistant."""

from __future__ import annotations

import logging
import sys
from typing import List, Optional, cast

from langchain_core.messages import AIMessage

from sleep_assistant.graph import build_app
from sleep_assistant.graph.state import ChatState, record_user_message

logger = logging.getLogger(__name__)


def run_cli(app=None) -> None:
    """Simple command-line interface to interact with the chatbot."""

    if app is None:
        app = build_app()

    print("Sleep Assistant ready! Type your message (or 'exit' to quit).")
    state: ChatState = {"messages": [], "user_history": []}

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        record_user_message(state, user_input)
        state = cast(ChatState, app.invoke(state))
        route = state.get("current_route") or state.get("route", "sleep")
        logger.info("Route used for latest turn: %s", route)

        state_messages = state.get("messages", [])
        ai_response = next(
            (message.content for message in reversed(state_messages) if isinstance(message, AIMessage)),
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
