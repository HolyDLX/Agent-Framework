"""Run actionlint when the project contains GitHub Actions workflows."""

import shutil
import subprocess
from pathlib import Path

from _framework import project_root
from _tool_runner import run_custom_tool


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("actionlint")
    if command is None:
        return 1
    workflows = root / ".github" / "workflows"
    if arguments:
        return subprocess.run([command, *arguments], cwd=root, check=False).returncode
    if not workflows.exists():
        return 0
    return subprocess.run([command], cwd=root, check=False).returncode


def main() -> int:
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
