"""Shared configuration helpers for loading environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from sleep_assistant import PROJECT_ROOT


def default_dotenv_path() -> Path:
    """Return the default .env location at the project root."""

    return PROJECT_ROOT / ".env"


def load_environment(*, override: bool = False) -> Optional[Path]:
    """Load environment variables from the project .env file if present."""

    dotenv_path = default_dotenv_path()
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=override)
        return dotenv_path

    # Fall back to default behavior (e.g., environment already configured)
    load_dotenv(override=override)
    return None


def require_env(name: str) -> str:
    """Fetch a required environment variable or exit with an error."""

    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch an environment variable with an optional default."""

    return os.environ.get(name, default)


__all__ = ["default_dotenv_path", "get_env", "load_environment", "require_env"]

