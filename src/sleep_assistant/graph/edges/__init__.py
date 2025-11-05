"""Helpers for wiring LangGraph edges within the chatbot application."""

from __future__ import annotations

from typing import Callable, Mapping

from langgraph.graph import END, StateGraph

from sleep_assistant.graph.state import ChatState

__all__ = ["configure_edges"]


def _default_route_selector(state: ChatState) -> str:
    """Return the next node name based on the route stored in graph state."""

    return state.get("current_route") or state.get("route", "general")


def configure_edges(
    graph: StateGraph,
    *,
    route_selector: Callable[[ChatState], str] | None = None,
    route_edges: Mapping[str, str] | None = None,
) -> None:
    """Attach the standard routing edges to the graph.

    Parameters
    ----------
    graph:
        The LangGraph state graph under construction.
    route_selector:
        Optional callable that selects the next node name from the current state.
        Defaults to using the route stored on the state.
    route_edges:
        Optional mapping that defines conditional edges from the router node.
        Defaults to mapping general → general and sleep → sleep.
    """

    selector = route_selector or _default_route_selector
    edges = dict(route_edges or {"general": "general", "sleep": "sleep"})

    graph.add_conditional_edges("router", selector, edges)
    graph.add_edge("general", END)
    graph.add_edge("sleep", END)
    graph.set_entry_point("router")
