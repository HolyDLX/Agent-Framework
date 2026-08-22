"""Run yamllint on project-owned YAML files."""

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _framework import project_root
from _tool_runner import run_custom_tool, skip


def _local(arguments: list[str]) -> int:
    root = project_root()
    command = shutil.which("yamllint")
    if command is None:
        return 1
    if arguments:
        files = arguments
    else:
        files = [
            str(p.relative_to(root))
            for pattern in ("*.yml", "*.yaml")
            for p in root.rglob(pattern)
            if "agent-framework" not in p.parts and ".git" not in p.parts
        ]
    if not files:
        return skip("no YAML files found")
    return subprocess.run(
        [command, *sorted(set(files))], cwd=root, check=False
    ).returncode


def main() -> int:
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
