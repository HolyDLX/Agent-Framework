"""Run pydoclint against configured source paths."""

from pathlib import Path

from _framework import existing_paths, load_config, project_root
from _tool_runner import run_executable_tool


def main() -> int:
    cfg = load_config()
    paths = existing_paths(project_root(), cfg.source_paths)
    if not paths:
        return 0
    defaults = [
        "--style",
        "google",
        "--arg-type-hints-in-docstring",
        "false",
        "--check-return-types",
        "false",
        "--allow-init-docstring",
        "true",
        "--skip-checking-raises",
        "true",
        "--skip-checking-private-functions",
        "true",
        *paths,
    ]
    return run_executable_tool(Path(__file__), "pydoclint", defaults)


if __name__ == "__main__":
    raise SystemExit(main())
