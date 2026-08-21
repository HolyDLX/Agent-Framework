"""Shared project Markdown file discovery for documentation runners."""

from __future__ import annotations

from pathlib import Path

from _framework import FRAMEWORK_ROOT, project_root

_IGNORED_PARTS = frozenset(
    {
        ".git",
        ".idea",
        ".pytest_cache",
        ".pyright",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "_build",
        "build",
        "coverage",
        "dist",
        "htmlcov",
        "node_modules",
    }
)


def markdown_files(root: Path | None = None) -> list[str]:
    """Return project-owned Markdown files as stable project-relative paths."""
    project = (root or project_root()).resolve()
    consuming_project = project != FRAMEWORK_ROOT.resolve()
    result: list[str] = []

    for path in project.rglob("*.md"):
        relative = path.relative_to(project)
        if any(part in _IGNORED_PARTS for part in relative.parts):
            continue
        if consuming_project and relative.parts[0] == "agent-framework":
            continue
        result.append(relative.as_posix())

    return sorted(result)
