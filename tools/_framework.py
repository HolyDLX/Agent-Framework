"""Shared Agent Framework project discovery and configuration."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import tomllib

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]


def project_root() -> Path:
    """Return consuming project root, or framework root when standalone."""
    override = os.environ.get("AGENT_FRAMEWORK_PROJECT_ROOT")
    if override:
        return Path(override).resolve()

    parent = FRAMEWORK_ROOT.parent
    if (
        FRAMEWORK_ROOT.name == "agent-framework"
        and (parent / "agent-framework.toml").is_file()
    ):
        return parent.resolve()
    return FRAMEWORK_ROOT


def framework_tool_path(path: Path) -> str:
    """Return a path usable from /workspace in the development container."""
    relative = path.resolve().relative_to(FRAMEWORK_ROOT)
    root = project_root()
    if root == FRAMEWORK_ROOT:
        return relative.as_posix()
    return (Path("agent-framework") / relative).as_posix()


def _strings(value: object, default: tuple[str, ...]) -> tuple[str, ...]:
    """Return a validated tuple of strings or the supplied default."""
    if not isinstance(value, list):
        return default

    items = cast(list[object], value)
    result: list[str] = []
    for item in items:
        if not isinstance(item, str):
            return default
        result.append(item)
    return tuple(result)


def _table(value: object) -> dict[str, object]:
    """Return a string-keyed TOML table or an empty table."""
    if not isinstance(value, dict):
        return {}

    table = cast(dict[object, object], value)
    return {key: item for key, item in table.items() if isinstance(key, str)}


@dataclass(frozen=True)
class FrameworkConfig:
    name: str
    python_version: str
    source_paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    docs_path: str
    readme: str
    coverage_min: int
    coverage_exclude_paths: tuple[str, ...]
    line_length: int
    exclude_paths: tuple[str, ...]


def load_config(root: Path | None = None) -> FrameworkConfig:
    """Load supported project inputs with opinionated defaults."""
    root = (root or project_root()).resolve()
    path = root / "agent-framework.toml"
    raw: dict[str, object] = {}
    if path.exists():
        parsed: object = tomllib.loads(path.read_text(encoding="utf-8"))
        raw = _table(parsed)

    project = _table(raw.get("project"))
    verification = _table(raw.get("verification"))

    name = project.get("name")
    if not isinstance(name, str) or not name.strip():
        name = root.name
    python_version = project.get("python_version", "3.12")
    if not isinstance(python_version, str):
        python_version = "3.12"
    docs_path = project.get("docs_path", "docs")
    readme = project.get("readme", "README.md")
    if not isinstance(docs_path, str):
        docs_path = "docs"
    if not isinstance(readme, str):
        readme = "README.md"

    coverage_min = verification.get("coverage_min", 90)
    line_length = verification.get("line_length", 88)
    if not isinstance(coverage_min, int):
        coverage_min = 90
    if not isinstance(line_length, int):
        line_length = 88

    return FrameworkConfig(
        name=name.strip(),
        python_version=python_version,
        source_paths=_strings(project.get("source_paths"), ("src",)),
        test_paths=_strings(project.get("test_paths"), ("tests",)),
        docs_path=docs_path,
        readme=readme,
        coverage_min=coverage_min,
        coverage_exclude_paths=_strings(
            verification.get("coverage_exclude_paths"),
            (),
        ),
        line_length=line_length,
        exclude_paths=_strings(
            verification.get("exclude_paths"),
            (".git", ".venv", "agent-framework", "coverage"),
        ),
    )


def existing_paths(root: Path, paths: tuple[str, ...]) -> list[str]:
    """Return configured paths that exist, preserving configured spelling."""
    return [path for path in paths if (root / path).exists()]


def has_project_tool_config(tool: str, root: Path | None = None) -> bool:
    """Return whether pyproject.toml contains a local table for one tool."""

    path = (root or project_root()) / "pyproject.toml"
    if not path.is_file():
        return False
    parsed = _table(tomllib.loads(path.read_text(encoding="utf-8")))
    return tool in _table(parsed.get("tool"))


def black_target_version(config: FrameworkConfig | None = None) -> str:
    """Return Black target-version spelling for the configured Python version."""
    version = (config or load_config()).python_version.strip()
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.\d+)?", version)
    if match is None:
        raise ValueError(
            "project.python_version must use numeric major.minor syntax "
            f"for Black targeting, got {version!r}"
        )
    major, minor = match.groups()
    return f"py{major}{minor}"


def project_image_name(config: FrameworkConfig | None = None) -> str:
    """Return deterministic local development-image name."""
    name = (config or load_config()).name.lower()
    slug = re.sub(r"[^a-z0-9_.-]+", "-", name).strip("-._") or "project"
    return f"agent-{slug}-development"
