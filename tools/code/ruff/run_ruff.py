"""Run Ruff against configured Python paths."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _framework import (
    existing_paths,
    has_project_tool_config,
    load_config,
    project_root,
)
from _tool_runner import run_custom_tool


def _run(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="apply Ruff's safe automatic fixes",
    )
    args = parser.parse_args(arguments)

    cfg = load_config()
    root = project_root()
    extra = ("tools",) if (root / "tools").exists() else ()
    paths = existing_paths(root, cfg.source_paths + cfg.test_paths + extra)

    command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
    ]
    has_local = has_project_tool_config("ruff", root)
    if not has_local:
        command.append("--extend-ignore=EXE002")

    if args.fix:
        command.append("--fix")

    command.extend(paths or ["."])

    return subprocess.run(command, cwd=root, check=False).returncode


def main() -> int:
    """Run Ruff with framework-owned cross-platform defaults."""
    return run_custom_tool(Path(__file__), _run)


if __name__ == "__main__":
    raise SystemExit(main())
