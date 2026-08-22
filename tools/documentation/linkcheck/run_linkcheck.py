"""Validate project-owned Markdown links without network access."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _documentation import markdown_files
from _framework import project_root
from _tool_runner import run_custom_tool, skip


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("lychee")
    if command is None:
        print("Executable not available: lychee")
        return 1

    files = arguments or markdown_files(root)
    if not files:
        return skip("no project-owned Markdown files found")

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
