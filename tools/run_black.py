"""Run Black against configured Python paths."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _framework import (
    black_target_version,
    existing_paths,
    load_config,
    project_root,
)
from _tool_runner import run_custom_tool


def _run(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="reformat files instead of checking formatting",
    )
    args = parser.parse_args(arguments)

    cfg = load_config()
    root = project_root()
    extra = ("tools",) if (root / "tools").exists() else ()
    paths = existing_paths(root, cfg.source_paths + cfg.test_paths + extra)

    command = [
        sys.executable,
        "-m",
        "black",
        f"--line-length={cfg.line_length}",
        "--target-version",
        black_target_version(cfg),
    ]

    if not args.fix:
        command.append("--check")

    command.extend(paths or ["."])

    return subprocess.run(command, cwd=root, check=False).returncode


def main() -> int:
    """Run Black with framework-owned project targeting."""
    return run_custom_tool(Path(__file__), _run)


if __name__ == "__main__":
    raise SystemExit(main())
