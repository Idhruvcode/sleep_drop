"""Factories for language and embedding models."""

from __future__ import annotations

from typing import Any, Optional

import httpx
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from sleep_assistant.config import get_env, require_env


def _normalize_base_url(base_url: Optional[str]) -> Optional[str]:
    return base_url.rstrip("/") if base_url else None


def _resolve_proxy_url() -> Optional[str]:
    """Return the first configured proxy URL, if any."""

    for env_name in ("OPENAI_PROXY", "OPENAI_HTTP_PROXY", "HTTPS_PROXY", "HTTP_PROXY"):
        proxy = get_env(env_name)
        if proxy:
            return proxy.strip()
    return None


def _build_openai_client_kwargs(api_key: str, base_url: Optional[str]) -> dict[str, Any]:
    """Create kwargs shared by ChatOpenAI and OpenAIEmbeddings."""

    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    proxy_url = _resolve_proxy_url()
    http_client_kwargs: dict[str, Any] = {"follow_redirects": True}
    if proxy_url:
        http_client_kwargs["proxy"] = proxy_url
    kwargs["http_client"] = httpx.Client(**http_client_kwargs)
    kwargs["http_async_client"] = httpx.AsyncClient(**http_client_kwargs)

    return kwargs


def _build_embedder(model_name: str, client_kwargs: dict[str, Any]) -> OpenAIEmbeddings:
    kwargs = {"model": model_name, **client_kwargs}
    return OpenAIEmbeddings(**kwargs)  # type: ignore[arg-type]


def build_chat_models() -> tuple[ChatOpenAI, ChatOpenAI, OpenAIEmbeddings]:
    """Instantiate chat and embedding models with shared credentials."""

    api_key = require_env("OPENAI_API_KEY")
    base_url = _normalize_base_url(get_env("OPENAI_BASE_URL"))
    chat_model_name = get_env("CHAT_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    embedding_model_name = get_env("EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"

    base_client_kwargs = _build_openai_client_kwargs(api_key, base_url)
    chat_kwargs = {**base_client_kwargs, "temperature": 0.3}

    general_llm = ChatOpenAI(model=chat_model_name, **chat_kwargs)
    sleep_llm = ChatOpenAI(model=chat_model_name, **chat_kwargs)

    embedder = _build_embedder(embedding_model_name, base_client_kwargs)
    return general_llm, sleep_llm, embedder


def build_embedder() -> OpenAIEmbeddings:
    """Instantiate just the embedding model (used by ingestion scripts)."""

    api_key = require_env("OPENAI_API_KEY")
    base_url = _normalize_base_url(get_env("OPENAI_BASE_URL"))
    embedding_model_name = get_env("EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"
    client_kwargs = _build_openai_client_kwargs(api_key, base_url)
    return _build_embedder(embedding_model_name, client_kwargs)


__all__ = ["build_chat_models", "build_embedder"]
