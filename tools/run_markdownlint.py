"""Lint project-owned Markdown files with markdownlint-cli2."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from _documentation import markdown_files
from _framework import project_root
from _tool_runner import run_custom_tool

_CONFIG = Path(__file__).with_name("markdownlint-cli2.yaml")


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("markdownlint-cli2")
    if command is None:
        print("Executable not available: markdownlint-cli2")
        return 1

    fix = "--fix" in arguments
    requested = [argument for argument in arguments if argument != "--fix"]
    files = requested or markdown_files(root)
    if not files:
        print("markdownlint skipped: no project-owned Markdown files")
        return 0

    command_line = [command, "--config", str(_CONFIG)]
    if fix:
        command_line.append("--fix")
    command_line.extend(files)
    return subprocess.run(command_line, cwd=root, check=False).returncode


def main() -> int:
    """Run Markdown linting, optionally applying deterministic fixes."""
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
