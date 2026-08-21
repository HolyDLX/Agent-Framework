"""Run pytest against configured test paths."""

from pathlib import Path

from _framework import existing_paths, load_config, project_root
from _tool_runner import run_python_tool


def main() -> int:
    cfg = load_config()
    paths = existing_paths(project_root(), cfg.test_paths)
    return run_python_tool(Path(__file__), "pytest", paths)


if __name__ == "__main__":
    raise SystemExit(main())
