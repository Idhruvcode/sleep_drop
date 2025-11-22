"""Project-wide logging configuration helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sleep_assistant import PROJECT_ROOT
from sleep_assistant.config import get_env

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "sleep_assistant.log"

_CONFIGURED = False


def _normalize_log_path(log_path: str | Path | None) -> Path:
    """Return an absolute path for the log file, creating parent dirs."""

    if not log_path:
        target = DEFAULT_LOG_FILE
    else:
        path_obj = Path(log_path)
        target = path_obj if path_obj.is_absolute() else PROJECT_ROOT / path_obj

    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _parse_level(value: Optional[str]) -> int:
    """Convert user-provided level strings into logging constants."""

    if not value:
        return logging.INFO
    if isinstance(value, str):
        numeric = logging.getLevelName(value.upper())
        if isinstance(numeric, int):
            return numeric
    return logging.INFO


def configure_logging(*, level: Optional[str] = None, log_file: Optional[str | Path] = None) -> Path:
    """Configure root logging to emit to both console and a rolling log file."""

    global _CONFIGURED
    if _CONFIGURED:
        return _normalize_log_path(log_file or get_env("LOG_FILE"))

    env_level = get_env("LOG_LEVEL")
    env_path = get_env("LOG_FILE")

    resolved_level = _parse_level(level or env_level)
    resolved_path = _normalize_log_path(log_file or env_path)

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(resolved_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    root_logger.setLevel(resolved_level)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    _CONFIGURED = True
    return resolved_path


__all__ = ["configure_logging"]
