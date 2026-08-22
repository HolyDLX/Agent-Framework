"""Manage Agent Framework tools enabled for this project."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from string import Template

TOOLS = Path(__file__).resolve().parent / "tools"
sys.path.insert(0, str(TOOLS))

from _framework import black_target_version, load_config, project_root
from _tool_catalog import Catalog, CatalogError, ToolBundle, discover_catalog
from _tool_config import load_assignments, write_assignments


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("status")
    enable = commands.add_parser("enable")
    enable.add_argument("tool")
    enable.add_argument("--in-category")
    enable.add_argument("--with-defaults", action="store_true")
    disable = commands.add_parser("disable")
    disable.add_argument("tool")
    disable.add_argument("--in-category")
    commands.add_parser("fix-duplicates")
    for name in ("show-defaults", "diff-defaults"):
        command = commands.add_parser(name)
        command.add_argument("tool", nargs="?")
    reset = commands.add_parser("reset-defaults")
    reset.add_argument("tool")
    reset.add_argument("--force", action="store_true")
    return parser


def _render_default(path: Path, root: Path) -> str:
    config = load_config(root)
    values = {
        "project_name": config.name,
        "python_version": config.python_version,
        "black_target": black_target_version(config),
        "line_length": str(config.line_length),
    }
    return Template(path.read_text(encoding="utf-8")).safe_substitute(values)


def _section_ranges(text: str, section: str) -> list[tuple[int, int]]:
    lines = text.splitlines(keepends=True)
    headers: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"\s*\[([^\]]+)]\s*(?:#.*)?$", line)
        if match:
            headers.append((index, match.group(1).strip()))
    ranges: list[tuple[int, int]] = []
    for position, (start, name) in enumerate(headers):
        if name != section and not name.startswith(section + "."):
            continue
        end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
        ranges.append((start, end))
    return ranges


def _extract_section(text: str, section: str) -> str | None:
    lines = text.splitlines(keepends=True)
    ranges = _section_ranges(text, section)
    if not ranges:
        return None
    return "".join("".join(lines[start:end]) for start, end in ranges).rstrip() + "\n"


def _replace_section(text: str, section: str, replacement: str) -> str:
    lines = text.splitlines(keepends=True)
    ranges = _section_ranges(text, section)
    if not ranges:
        return text.rstrip() + "\n\n" + replacement.rstrip() + "\n"
    remove = {index for start, end in ranges for index in range(start, end)}
    retained = "".join(line for index, line in enumerate(lines) if index not in remove)
    return retained.rstrip() + "\n\n" + replacement.rstrip() + "\n"


def _local_artifact(root: Path, tool: ToolBundle) -> bool:
    for artifact in tool.configuration:
        target = root / artifact.target
        if not target.is_file():
            continue
        if artifact.section is None:
            return True
        if _extract_section(target.read_text(encoding="utf-8"), artifact.section):
            return True
    return False


def _configuration_status(root: Path, tool: ToolBundle) -> str:
    if not tool.configuration:
        return "no"
    present = 0
    for artifact in tool.configuration:
        target = root / artifact.target
        if not target.is_file():
            continue
        if artifact.section is None or _extract_section(
            target.read_text(encoding="utf-8"), artifact.section
        ):
            present += 1
    if present == 0:
        return "no"
    return "yes" if present == len(tool.configuration) else "partial"


def _deploy_defaults(root: Path, tool: ToolBundle, *, force: bool) -> list[str]:
    changed: list[str] = []
    planned: dict[Path, str] = {}
    for artifact in tool.configuration:
        target = root / artifact.target
        default = _render_default(artifact.default, root)
        if artifact.section is None:
            if target.exists() and not force:
                continue
            planned[target] = default
            changed.append(artifact.target.as_posix())
            continue
        if target in planned:
            existing = planned[target]
        else:
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
        if _extract_section(existing, artifact.section) is not None and not force:
            continue
        planned[target] = _replace_section(existing, artifact.section, default)
        changed.append(f"{artifact.target.as_posix()} [{artifact.section}]")
    for target, content in planned.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
    return changed


def _resolve_configured(
    value: str, catalog: Catalog, assignments: dict[str, list[str]]
) -> str:
    try:
        return catalog.resolve(value).identifier
    except CatalogError:
        normalized = value.strip().lower().replace("\\", "/")
        configured = {item for items in assignments.values() for item in items}
        if "/" in normalized and normalized in configured:
            return normalized
        matches = [item for item in configured if item.rsplit("/", 1)[-1] == normalized]
        if len(matches) == 1:
            return matches[0]
        raise


def _list(catalog: Catalog) -> int:
    print("Available tools:")
    for tool in catalog.tools.values():
        operations = ", ".join(tool.operations)
        print(f"  {tool.identifier:<36} {tool.display_name} ({operations})")
    for error in catalog.errors:
        print(f"WARNING: Invalid bundle: {error}")
    return 0


def _status(root: Path, catalog: Catalog, assignments: dict[str, list[str]]) -> int:
    assigned: dict[str, list[str]] = {}
    for category, tool_names in assignments.items():
        for identifier in dict.fromkeys(tool_names):
            assigned.setdefault(identifier, []).append(category)
    print("Enabled tools:")
    duplicates: list[tuple[str, str]] = []
    for category, tool_names in assignments.items():
        seen: set[str] = set()
        for identifier in tool_names:
            if identifier in seen:
                duplicates.append((category, identifier))
            seen.add(identifier)
    for identifier, categories in assigned.items():
        tool = catalog.tools.get(identifier)
        availability = "available" if tool else "UNAVAILABLE"
        local = _configuration_status(root, tool) if tool else "unknown"
        print(f"  {identifier}")
        print(f"    Categories: {', '.join(categories)}")
        print(f"    Availability: {availability}")
        print(f"    Local configuration: {local}")
    print("\nAvailable but disabled:")
    for identifier, tool in catalog.tools.items():
        if identifier not in assigned:
            local = (
                " (local configuration present)" if _local_artifact(root, tool) else ""
            )
            print(f"  {identifier}{local}")
    for error in catalog.errors:
        print(f"WARNING: Invalid bundle: {error}")
    for category, identifier in duplicates:
        print(f"WARNING: Duplicate assignment: {identifier} in {category}")
    return 1 if any(identifier not in catalog.tools for identifier in assigned) else 0


def _selected_tools(value: str | None, catalog: Catalog) -> list[ToolBundle]:
    return [catalog.resolve(value)] if value else list(catalog.tools.values())


def _show_defaults(root: Path, selected: list[ToolBundle]) -> int:
    for tool in selected:
        print(tool.identifier)
        if not tool.configuration:
            print("  No framework defaults.\n")
            continue
        for artifact in tool.configuration:
            suffix = f" [{artifact.section}]" if artifact.section else ""
            print(f"  Target: {artifact.target.as_posix()}{suffix}\n")
            print(_render_default(artifact.default, root).rstrip())
            print()
    return 0


def _diff_defaults(root: Path, selected: list[ToolBundle]) -> int:
    for tool in selected:
        for artifact in tool.configuration:
            target = root / artifact.target
            default = _render_default(artifact.default, root)
            local: str | None = None
            if target.is_file():
                text = target.read_text(encoding="utf-8")
                local = (
                    text
                    if artifact.section is None
                    else _extract_section(text, artifact.section)
                )
            if local is None:
                print(f"{tool.identifier}: using bundle defaults")
                continue
            difference = list(
                difflib.unified_diff(
                    default.splitlines(),
                    local.splitlines(),
                    fromfile="bundle-default",
                    tofile=str(artifact.target),
                    lineterm="",
                )
            )
            if difference:
                print(f"{tool.identifier}: {artifact.target}")
                print("\n".join(difference))
            else:
                print(f"{tool.identifier}: no differences")
    return 0


def main(arguments: list[str] | None = None) -> int:
    """Run the project tool-management CLI."""

    args = _parser().parse_args(arguments)
    root = project_root()
    catalog = discover_catalog()
    try:
        assignments = load_assignments(root)
        if args.command == "list":
            return _list(catalog)
        if args.command == "status":
            return _status(root, catalog, assignments)
        if args.command == "fix-duplicates":
            removed = 0
            for category, values in assignments.items():
                unique = list(dict.fromkeys(values))
                removed += len(values) - len(unique)
                assignments[category] = unique
            if removed:
                write_assignments(root, assignments)
            print(f"Removed {removed} duplicate assignment(s).")
            return 0
        if args.command in {"show-defaults", "diff-defaults"}:
            selected = _selected_tools(args.tool, catalog)
            return (
                _show_defaults(root, selected)
                if args.command == "show-defaults"
                else _diff_defaults(root, selected)
            )
        tool = catalog.resolve(args.tool) if args.command != "disable" else None
        if args.command == "enable":
            assert tool is not None
            category = (
                tool.native_category
                if args.in_category is None
                else args.in_category.strip().lower()
            )
            if category not in catalog.categories:
                choices = ", ".join(catalog.categories)
                raise CatalogError(
                    f"Unknown category {category!r}. Available: {choices}"
                )
            values = assignments.setdefault(category, [])
            if tool.identifier in values:
                print(
                    f"{tool.identifier} is already enabled in {category}. Nothing changed."
                )
            else:
                values.append(tool.identifier)
                write_assignments(root, assignments)
                print(f"Enabled {tool.identifier} in {category}.")
            if args.with_defaults:
                changed = _deploy_defaults(root, tool, force=False)
                print(f"Deployed {len(changed)} default configuration artifact(s).")
            return 0
        if args.command == "disable":
            identifier = _resolve_configured(args.tool, catalog, assignments)
            available = catalog.tools.get(identifier)
            native = (
                identifier.split("/", 1)[0]
                if available is None
                else available.native_category
            )
            category = (
                native if args.in_category is None else args.in_category.strip().lower()
            )
            if category not in catalog.categories:
                choices = ", ".join(catalog.categories)
                raise CatalogError(
                    f"Unknown category {category!r}. Available: {choices}"
                )
            values = assignments.setdefault(category, [])
            count = values.count(identifier)
            assignments[category] = [item for item in values if item != identifier]
            if count:
                write_assignments(root, assignments)
            print(
                f"Disabled {identifier} in {category}; removed {count} assignment(s)."
            )
            remaining = [
                assigned_category
                for assigned_category, assigned_tools in assignments.items()
                if identifier in assigned_tools
            ]
            if remaining:
                print(f"Still enabled in: {', '.join(remaining)}")
            if available and _local_artifact(root, available):
                print("WARNING: Local tool configuration remains and was not removed.")
            if available is None:
                print(
                    "WARNING: Tool metadata is unavailable; configuration could not be identified."
                )
            return 0
        if args.command == "reset-defaults":
            assert tool is not None
            if _local_artifact(root, tool) and not args.force:
                print(
                    "Local configuration exists; use --force to replace it.",
                    file=sys.stderr,
                )
                return 2
            changed = _deploy_defaults(root, tool, force=True)
            print(f"Reset {len(changed)} default configuration artifact(s).")
            return 0
    except CatalogError as exc:
        print(str(exc), file=sys.stderr)
        _list(catalog)
        return 2
    except (OSError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
