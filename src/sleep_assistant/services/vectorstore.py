"""Factories for vector store integrations."""

from __future__ import annotations

import logging
from typing import Any, Optional

from pinecone import Pinecone

from sleep_assistant.config import get_env, require_env

logger = logging.getLogger(__name__)


def build_pinecone_index(pinecone_client: Pinecone) -> Any:
    """Return a Pinecone index handle ensuring accessibility."""

    index_name = require_env("PINECONE_INDEX_NAME")
    index_host: Optional[str] = (
        get_env("PINECONE_INDEX_HOST") or get_env("PINECONE_HOST_NAME") or get_env("PINECONE_INDEX_URL")
    )

    try:
        pinecone_client.describe_index(index_name)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"Pinecone index '{index_name}' is not accessible: {exc}"
        ) from exc

    kwargs = {"name": index_name}
    if index_host:
        kwargs["host"] = index_host
        logger.info("Using Pinecone index '%s' at host '%s'", index_name, index_host)
    else:
        logger.warning(
            "No Pinecone host provided. For serverless indexes set PINECONE_INDEX_HOST or PINECONE_HOST_NAME."
        )

    return pinecone_client.Index(**kwargs)


__all__ = ["build_pinecone_index"]

