"""Check or regenerate contract requirement/traceability artifacts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _framework import FRAMEWORK_ROOT, project_root
from _tool_runner import run_custom_tool


def _local(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="regenerate generated contract artifacts",
    )
    args = parser.parse_args(arguments)

    root = project_root()
    script = FRAMEWORK_ROOT / "tools" / "contracts" / "generate_traceability.py"

    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(root),
    ]

    if not args.fix:
        command.append("--check")

    return subprocess.run(command, cwd=root, check=False).returncode


def main() -> int:
    """Check or regenerate contract artifacts."""
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
