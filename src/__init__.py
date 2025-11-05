"""Backward-compatible package shim for the Sleep Assistant project.

Prefer importing from :mod:`sleep_assistant` directly.
"""

from __future__ import annotations

from sleep_assistant import PACKAGE_ROOT, PROJECT_ROOT, build_app  # noqa: F401

__all__ = ["PACKAGE_ROOT", "PROJECT_ROOT", "build_app"]
