"""Factories for language and embedding models."""

from __future__ import annotations

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
 
from sleep_assistant.config import get_env, require_env


def build_chat_models() -> tuple[ChatOpenAI, ChatOpenAI, OpenAIEmbeddings]:
    """Instantiate chat and embedding models with shared credentials."""

    api_key = require_env("OPENAI_API_KEY")
    base_url = get_env("OPENAI_BASE_URL")
    chat_model_name = get_env("CHAT_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    embedding_model_name = get_env("EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"

    client_kwargs = {"api_key": api_key, "temperature": 0.3}
    if base_url:
        client_kwargs["base_url"] = base_url.rstrip("/")

    general_llm = ChatOpenAI(model=chat_model_name, **client_kwargs)
    sleep_llm = ChatOpenAI(model=chat_model_name, **client_kwargs)

    embedder = OpenAIEmbeddings(model=embedding_model_name, api_key=api_key)  # type: ignore[arg-type]
    if base_url:
        embedder = OpenAIEmbeddings(model=embedding_model_name, api_key=api_key, base_url=base_url.rstrip("/"))  # type: ignore[arg-type]
    return general_llm, sleep_llm, embedder


__all__ = ["build_chat_models"]

