"""Shared command-line handling for Agent Framework runners."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from _framework import project_root
from container.docker_helper import run_in_container
from container.local_execution import (
    assert_local_execution_allowed,
    is_running_in_container,
)


def _write_result(status: str, reason: str | None = None) -> None:
    path = os.environ.get("AGENT_FRAMEWORK_RESULT_FILE")
    if not path:
        return
    result_path = Path(path)
    if result_path.exists():
        return
    result_path.write_text(
        json.dumps({"status": status, "reason": reason}), encoding="utf-8"
    )


def skip(reason: str) -> int:
    """Report a successful non-applicable tool invocation."""

    print(reason)
    _write_result("skip", reason)
    return 0


def _run_tool(
    script: Path, local_runner: Callable[[list[str]], int], defaults: Sequence[str]
) -> int:
    arguments = sys.argv[1:]
    container = "--container" in arguments
    if container:
        arguments.remove("--container")
        if not is_running_in_container():
            return run_in_container(script, arguments or list(defaults))
    if not is_running_in_container():
        assert_local_execution_allowed()
    result = local_runner(arguments or list(defaults))
    _write_result("pass" if result == 0 else "fail")
    return result


def run_python_tool(script: Path, module: str, defaults: Sequence[str]) -> int:
    def local(arguments: list[str]) -> int:
        if importlib.util.find_spec(module) is None:
            print(f"Python module not available: {module}")
            return 1
        return subprocess.run(
            [sys.executable, "-m", module, *arguments], cwd=project_root(), check=False
        ).returncode

    return _run_tool(script, local, defaults)


def run_executable_tool(script: Path, executable: str, defaults: Sequence[str]) -> int:
    def local(arguments: list[str]) -> int:
        command = shutil.which(executable)
        if command is None:
            print(f"Executable not available: {executable}")
            return 1
        return subprocess.run(
            [command, *arguments], cwd=project_root(), check=False
        ).returncode

    return _run_tool(script, local, defaults)


def run_custom_tool(
    script: Path, local_runner: Callable[[list[str]], int], defaults: Sequence[str] = ()
) -> int:
    return _run_tool(script, local_runner, defaults)
