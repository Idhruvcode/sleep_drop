"""MongoDB Atlas Vector Search helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

from sleep_assistant.config import get_env, require_env

logger = logging.getLogger(__name__)


@dataclass
class VectorMatch:
    """Single match returned from a vector search query."""

    metadata: dict[str, Any]
    score: float | None = None


@dataclass
class VectorQueryResult:
    """Container for matches to mirror the legacy vector store response shape."""

    matches: list[VectorMatch]


class MongoVectorStore:
    """Thin wrapper around a MongoDB collection with a vector search index."""

    def __init__(
        self,
        collection: Collection,
        *,
        index_name: str,
        embedding_field: str = "embedding",
        num_candidates: int | None = None,
    ) -> None:
        self._collection = collection
        self._index_name = index_name
        self._embedding_field = embedding_field
        self._num_candidates = num_candidates

    def query(
        self,
        vector: Sequence[float],
        *,
        top_k: int = 5,
        include_metadata: bool = True,  # kept for signature parity
    ) -> VectorQueryResult:
        """Execute a MongoDB Atlas vector search and normalize the result."""

        if not vector:
            logger.warning("Skipping MongoDB vector query because the query vector was empty.")
            return VectorQueryResult(matches=[])

        limit = max(1, top_k)
        num_candidates = self._num_candidates or max(limit * 5, limit)
        query_vector = [float(value) for value in vector]

        pipeline: list[dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": self._index_name,
                    "path": self._embedding_field,
                    "queryVector": query_vector,
                    "numCandidates": num_candidates,
                    "limit": limit,
                }
            },
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
        ]

        if include_metadata:
            pipeline.append({"$project": {"_id": 0, "score": 1, "metadata": "$$ROOT"}})
        else:
            pipeline.append({"$project": {"_id": 0, "score": 1}})

        docs = list(self._collection.aggregate(pipeline))
        matches: list[VectorMatch] = []
        for doc in docs:
            score = _coerce_float(doc.get("score"))
            metadata: dict[str, Any] = {}
            if include_metadata:
                raw_metadata = doc.get("metadata")
                if isinstance(raw_metadata, dict):
                    metadata = dict(raw_metadata)  # shallow copy
                    metadata.pop("score", None)
                    metadata.pop(self._embedding_field, None)
                    metadata.pop("_id", None)
            matches.append(VectorMatch(metadata=metadata, score=score))

        return VectorQueryResult(matches=matches)


def _coerce_float(value: Any) -> float | None:
    """Best-effort conversion to float."""

    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_int_env(name: str) -> int | None:
    raw_value = get_env(name)
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError as exc:
        raise SystemExit(f"Environment variable {name} must be an integer.") from exc


def build_mongo_vector_store(client: MongoClient) -> MongoVectorStore:
    """Resolve configuration and return a Mongo-backed vector store."""

    database_name = require_env("MONGODB_DBNAME")
    collection_name = require_env("MONGODB_COLLECTION")
    index_name = get_env("MONGODB_VECTOR_INDEX", "vector_index") or "vector_index"
    embedding_field = get_env("MONGODB_EMBEDDING_FIELD", "embedding") or "embedding"
    num_candidates = _read_int_env("MONGODB_VECTOR_CANDIDATES")

    collection = client[database_name][collection_name]
    logger.info(
        "Using MongoDB vector collection '%s.%s' with index '%s' (embedding field '%s').",
        database_name,
        collection_name,
        index_name,
        embedding_field,
    )
    if num_candidates:
        logger.info("MongoDB vector search numCandidates set to %d.", num_candidates)

    return MongoVectorStore(
        collection,
        index_name=index_name,
        embedding_field=embedding_field,
        num_candidates=num_candidates,
    )


__all__ = ["MongoVectorStore", "VectorMatch", "VectorQueryResult", "build_mongo_vector_store"]
