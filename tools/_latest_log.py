"""Concise subprocess execution with an atomic latest-run log."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    output: str
    duration: float


def capture(
    command: list[str], *, cwd: Path, environment: dict[str, str] | None = None
) -> CommandResult:
    """Capture combined command output and duration without shell interpretation."""

    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return CommandResult(result.returncode, result.stdout, time.monotonic() - started)


def write_latest(path: Path, content: str) -> None:
    """Atomically replace one latest log."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def print_tail(output: str, *, lines: int = 40, width: int = 2000) -> None:
    """Print an uninterpreted bounded tail of captured output."""

    for line in output.splitlines()[-lines:]:
        print(line if len(line) <= width else line[:width] + "...")
