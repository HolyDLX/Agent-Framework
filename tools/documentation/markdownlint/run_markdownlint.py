"""Lint project-owned Markdown files with markdownlint-cli2."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _documentation import markdown_files
from _framework import project_root
from _tool_runner import run_custom_tool, skip

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
        return skip("no project-owned Markdown files found")

    local_config = root / ".markdownlint-cli2.yaml"
    config = local_config if local_config.is_file() else _CONFIG
    command_line = [command, "--config", str(config)]
    if fix:
        command_line.append("--fix")
    command_line.extend(files)
    return subprocess.run(command_line, cwd=root, check=False).returncode


def main() -> int:
    """Run Markdown linting, optionally applying deterministic fixes."""
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
