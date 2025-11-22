"""Launch the LangGraph-based sleep assistant CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_ROOT):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

from sleep_assistant.cli import main
from sleep_assistant.logging import configure_logging

configure_logging()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
