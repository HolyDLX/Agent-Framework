"""Run the tests category verify phase."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from _category_runner import main_for_category
from _tool_runner import run_custom_tool


def _local(arguments: list[str]) -> int:
    return main_for_category("tests", "verify", arguments)


if __name__ == "__main__":
    raise SystemExit(run_custom_tool(Path(__file__), _local))
