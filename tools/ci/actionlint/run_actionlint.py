"""Run actionlint when the project contains GitHub Actions workflows."""

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _framework import project_root
from _tool_runner import run_custom_tool, skip


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("actionlint")
    if command is None:
        return 1
    workflows = root / ".github" / "workflows"
    if arguments:
        return subprocess.run([command, *arguments], cwd=root, check=False).returncode
    if not workflows.exists():
        return skip("no GitHub Actions workflows found")
    return subprocess.run([command], cwd=root, check=False).returncode


def main() -> int:
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
