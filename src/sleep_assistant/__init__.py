"""Sleep Assistant application package built on LangGraph."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

from .graph.core import build_app  # noqa: E402

__all__ = ["build_app", "PACKAGE_ROOT", "PROJECT_ROOT"]

