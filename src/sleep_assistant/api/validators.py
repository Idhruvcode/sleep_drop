"""Utilities for pre-validating user chat messages before invoking the chatbot graph."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ValidationResult:
    """Represents the outcome of validating an incoming user message."""

    is_valid: bool
    error_message: Optional[str] = None


_MEANINGFUL_MIN_CHARACTERS = 3
_ALPHA_PATTERN = re.compile(r"[A-Za-z]")
_SAFE_PATTERNS = (
    re.compile(r"\b(?:kill|suicide|self-harm|weapon|bomb|attack)\b", re.IGNORECASE),
)

def _is_meaningful(message: str) -> bool:
    """Return True if the message contains sufficient content to consider."""

    if len(message) < _MEANINGFUL_MIN_CHARACTERS:
        return False
    return bool(_ALPHA_PATTERN.search(message))


def _is_safe(message: str) -> bool:
    """Return True if the message does not contain obvious unsafe intent."""

    return not any(pattern.search(message) for pattern in _SAFE_PATTERNS)


def validate_user_message(raw_message: str) -> ValidationResult:
    """Validate user input for basic meaning and safety checks."""

    message = raw_message.strip()
    if not message:
        return ValidationResult(
            is_valid=False,
            error_message="It looks like your message was empty. Please share a sleep-related question so I can help.",
        )

    if not _is_meaningful(message):
        return ValidationResult(
            is_valid=False,
            error_message="I need a bit more detail to help. Could you add a few more words about your sleep question?",
        )

    if not _is_safe(message):
        return ValidationResult(
            is_valid=False,
            error_message="I'm here to talk about healthy sleep habits. Please avoid harmful topics and try again.",
        )

    return ValidationResult(is_valid=True)


__all__ = ["ValidationResult", "validate_user_message"]
