"""MongoDB client helpers."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure

from sleep_assistant.config import get_env, require_env

logger = logging.getLogger(__name__)


def _resolve_mongo_uri() -> str:
    """Return the MongoDB connection string, building it from parts if needed."""

    direct_uri = get_env("MONGODB_URI")
    if direct_uri:
        return direct_uri

    username = require_env("MONGODB_USERNAME")
    password = require_env("MONGODB_PASSWORD")
    cluster = require_env("MONGODB_CLUSTER_URL")
    default_db = (get_env("MONGODB_DBNAME") or "").strip("/")

    user = quote_plus(username)
    pwd = quote_plus(password)
    uri = f"mongodb+srv://{user}:{pwd}@{cluster}"
    if default_db:
        uri = f"{uri}/{default_db}"

    options = get_env("MONGODB_URI_OPTIONS") or get_env("MONGODB_URI_PARAMS")
    if options:
        options = options.lstrip("?")
        uri = f"{uri}?{options}"

    return uri


def create_mongodb_client() -> MongoClient:
    """Instantiate a MongoDB client and verify connectivity."""

    uri = _resolve_mongo_uri()
    client_kwargs: dict[str, Any] = {"serverSelectionTimeoutMS": 5000}
    app_name = get_env("MONGODB_APP_NAME")
    if app_name:
        client_kwargs["appname"] = app_name

    try:
        client = MongoClient(uri, **client_kwargs)
        client.admin.command("ping")
    except (ConfigurationError, ConnectionFailure) as exc:
        raise SystemExit(f"Unable to connect to MongoDB cluster: {exc}") from exc

    logger.info("Connected to MongoDB cluster at '%s'.", uri.split("@")[-1])
    return client


__all__ = ["create_mongodb_client"]
