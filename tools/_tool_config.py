"""Read and update the machine-managed tool assignment configuration."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import tomllib
from _tool_catalog import normalize_identifier, normalize_tool_reference

BEGIN = "# BEGIN MANAGED TOOL CONFIGURATION"
END = "# END MANAGED TOOL CONFIGURATION"


def load_assignments(root: Path) -> dict[str, list[str]]:
    """Load ordered category assignments from agent-framework.toml."""

    path = root / "agent-framework.toml"
    parsed = tomllib.loads(path.read_text(encoding="utf-8"))
    raw_tools = parsed.get("tools", {})
    if not isinstance(raw_tools, dict):
        raise TypeError("[tools] must be a TOML table")
    assignments: dict[str, list[str]] = {}
    for raw_category, raw_value in cast(dict[object, object], raw_tools).items():
        if not isinstance(raw_category, str) or not isinstance(raw_value, dict):
            raise TypeError("Each tools category must be a TOML table")
        category = normalize_identifier(raw_category)
        enabled = cast(dict[object, object], raw_value).get("enabled", [])
        if not isinstance(enabled, list) or not all(
            isinstance(item, str) for item in cast(list[object], enabled)
        ):
            raise ValueError(f"tools.{category}.enabled must be an array of strings")
        assignments[category] = [
            normalize_tool_reference(cast(str, item))
            for item in cast(list[object], enabled)
        ]
    return assignments


def _render(assignments: dict[str, list[str]]) -> str:
    lines = [BEGIN]
    for category, enabled in assignments.items():
        lines.extend((f"[tools.{category}]", "enabled = ["))
        lines.extend(f'    "{tool}",' for tool in enabled)
        lines.extend(("]", ""))
    if lines[-1] == "":
        lines.pop()
    lines.append(END)
    return "\n".join(lines)


def write_assignments(root: Path, assignments: dict[str, list[str]]) -> None:
    """Atomically replace only the managed tool configuration section."""

    path = root / "agent-framework.toml"
    original = path.read_text(encoding="utf-8")
    managed = _render(assignments)
    if BEGIN in original or END in original:
        if original.count(BEGIN) != 1 or original.count(END) != 1:
            raise ValueError("Invalid managed tool configuration markers")
        before, remainder = original.split(BEGIN, 1)
        _, after = remainder.split(END, 1)
        updated = before.rstrip() + "\n\n" + managed + after
    else:
        updated = original.rstrip() + "\n\n" + managed + "\n"
    if updated == original:
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(path)
