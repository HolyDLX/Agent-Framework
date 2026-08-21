"""Validate project-owned Markdown links without network access."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from _documentation import markdown_files
from _framework import project_root
from _tool_runner import run_custom_tool


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("lychee")
    if command is None:
        print("Executable not available: lychee")
        return 1

    files = arguments or markdown_files(root)
    if not files:
        print("link check skipped: no project-owned Markdown files")
        return 0

    return subprocess.run(
        [
            command,
            "--offline",
            "--no-progress",
            "--include-fragments=anchor-only",
            "--root-dir",
            str(root),
            "--",
            *files,
        ],
        cwd=root,
        check=False,
    ).returncode


def main() -> int:
    """Check repository-local links in project-owned Markdown files."""
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
