"""Prompt template used for sleep-focused answers."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


def get_sleep_prompt() -> ChatPromptTemplate:
    """Return the prompt used to answer sleep-related questions."""

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a knowledgeable assistant that answers questions about sleep "
                "using the provided context. Cite relevant points from the context when possible. "
                "If the context lacks enough information, say so before offering general guidance.",
            ),
            (
                "human",
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Compose a helpful answer:",
            ),
        ]
    )


__all__ = ["get_sleep_prompt"]

