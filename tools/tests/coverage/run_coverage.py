"""Run pytest under coverage and emit terminal, HTML, and XML reports."""

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _framework import FrameworkConfig, existing_paths, load_config, project_root
from _tool_runner import run_custom_tool, skip


def _omit_arguments(config: FrameworkConfig) -> list[str]:
    """Return coverage.py omit arguments for configured coverage exclusions."""
    if not config.coverage_exclude_paths:
        return []
    return [f"--omit={','.join(config.coverage_exclude_paths)}"]


def _coverage_sources(root: Path, paths: tuple[str, ...]) -> list[str]:
    """Return coverage source spellings for configured directories or modules."""

    result: list[str] = []
    for path in existing_paths(root, paths):
        candidate = root / path
        if candidate.is_file() and candidate.suffix == ".py":
            result.append(Path(path).with_suffix("").as_posix().replace("/", "."))
        else:
            result.append(path)
    return result


def _local(arguments: list[str]) -> int:
    cfg = load_config()
    root = project_root()
    command = shutil.which("coverage")
    if command is None:
        return 1
    sources = _coverage_sources(root, cfg.source_paths)
    tests = existing_paths(root, cfg.test_paths)
    if not sources:
        return skip("no configured source paths found")
    omit_arguments = _omit_arguments(cfg)
    result = subprocess.run(
        [
            command,
            "run",
            "--branch",
            f"--source={','.join(sources)}",
            *omit_arguments,
            "-m",
            "pytest",
            *(arguments or tests),
        ],
        cwd=root,
        check=False,
    )
    if result.returncode:
        return result.returncode
    for cmd in (
        [command, "report", *omit_arguments, f"--fail-under={cfg.coverage_min}"],
        [command, "html", *omit_arguments, "--directory", "coverage/htmlcov"],
        [command, "xml", *omit_arguments, "-o", "coverage/coverage.xml"],
    ):
        result = subprocess.run(cmd, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    return 0


def main() -> int:
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
