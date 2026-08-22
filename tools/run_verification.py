"""Run configured Agent Framework verification categories."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _framework import project_root
from _latest_log import capture, print_tail, write_latest
from _tool_catalog import discover_catalog, normalize_identifier
from _tool_config import load_assignments
from _tool_runner import run_custom_tool


def _record_preflight_failure(root: Path, log_path: Path, message: str) -> None:
    try:
        write_latest(log_path, message + "\n")
    except OSError as exc:
        print(f"WARNING: Could not write log {log_path}: {exc}", file=sys.stderr)
        return
    print(f"Complete log: {log_path.relative_to(root)}", file=sys.stderr)


def _parse(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--ignore-unavailable", action="store_true")
    parser.add_argument("categories", nargs="*")
    return parser.parse_args(arguments)


def run_configured(arguments: list[str]) -> int:
    """Run configured categories for an already-selected execution environment."""
    parsed = _parse(arguments)
    root = project_root()
    log_path = root / ".agent-framework" / "logs" / "run_verification" / "latest.log"
    catalog = discover_catalog()
    try:
        assignments = load_assignments(root)
        categories = (
            [normalize_identifier(value) for value in parsed.categories]
            if parsed.categories
            else list(assignments)
        )
    except (OSError, TypeError, ValueError) as exc:
        message = f"Invalid tool configuration: {exc}"
        print(message, file=sys.stderr)
        _record_preflight_failure(root, log_path, message)
        return 2

    unknown = [item for item in categories if item not in catalog.categories]
    if unknown:
        message = "Unknown configured categories: " + ", ".join(unknown)
        print(message, file=sys.stderr)
        _record_preflight_failure(root, log_path, message)
        return 2
    unavailable = [
        tool
        for category in categories
        for tool in assignments.get(category, [])
        if tool not in catalog.tools
    ]
    if unavailable and not parsed.ignore_unavailable:
        messages = ["Enabled tools are unavailable:"]
        messages.extend(f"  {identifier}" for identifier in dict.fromkeys(unavailable))
        messages.append("Use --ignore-unavailable to skip them.")
        message = "\n".join(messages)
        print(message, file=sys.stderr)
        _record_preflight_failure(root, log_path, message)
        return 2

    phases = ["fix", "verify"] if parsed.fix else ["verify"]
    failed = False
    aggregate: list[str] = []
    for operation in phases:
        print(f"\n{operation.title()} phase:")
        aggregate.append(f"{operation.title()} phase:")
        for category_name in categories:
            category = catalog.categories[category_name]
            entry = category.fix if operation == "fix" else category.verify
            command = [sys.executable, str(entry), "--_emit-full-output"]
            if parsed.verbose:
                command.append("--verbose")
            if parsed.ignore_unavailable:
                command.append("--ignore-unavailable")
            result = capture(command, cwd=root)
            status = "PASS" if result.returncode == 0 else "FAIL"
            summary = f"{status:<5} {category_name:<24} {result.duration:.1f}s"
            print(summary)
            aggregate.extend(("", summary, result.output.rstrip()))
            if parsed.verbose and result.output:
                print(result.output, end="" if result.output.endswith("\n") else "\n")
            failed = failed or result.returncode != 0

    try:
        write_latest(log_path, "\n".join(aggregate).rstrip() + "\n")
    except OSError as exc:
        print(f"WARNING: Could not write log {log_path}: {exc}")
    if failed:
        if not parsed.verbose:
            print("\nLast 40 log lines:")
            print_tail("\n".join(aggregate))
        print(f"\nComplete log: {log_path.relative_to(root)}")
    return 1 if failed else 0


def main() -> int:
    """Apply optional fixes and run configured verification."""

    return run_custom_tool(Path(__file__), run_configured)


if __name__ == "__main__":
    raise SystemExit(main())
