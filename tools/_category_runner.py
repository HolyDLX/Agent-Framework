"""Execute configured tools assigned to one verification category."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from _framework import project_root
from _latest_log import capture, print_tail, write_latest
from _tool_catalog import CatalogError, discover_catalog
from _tool_config import load_assignments


def _parse(category: str, operation: str, arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Run {operation} operations assigned to {category}."
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--ignore-unavailable", action="store_true")
    parser.add_argument(
        "--_emit-full-output", action="store_true", help=argparse.SUPPRESS
    )
    return parser.parse_args(arguments)


def _result(path: Path, returncode: int) -> tuple[str, str | None]:
    if not path.is_file():
        return ("pass" if returncode == 0 else "fail", None)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ("pass" if returncode == 0 else "fail", None)
    status = data.get("status")
    reason = data.get("reason")
    if status not in {"pass", "fail", "skip"}:
        return ("pass" if returncode == 0 else "fail", None)
    return status, reason if isinstance(reason, str) else None


def run_category(category: str, operation: str, arguments: argparse.Namespace) -> int:
    """Run one configured category phase and return its combined status."""

    root = project_root()
    catalog = discover_catalog()
    discovered_category = catalog.categories.get(category)
    if discovered_category is None:
        print(f"Unknown category: {category}", file=sys.stderr)
        return 2
    try:
        assignments = load_assignments(root)
    except (OSError, TypeError, ValueError) as exc:
        print(f"Invalid agent-framework.toml: {exc}", file=sys.stderr)
        return 2
    configured = assignments.get(category, [])
    seen: set[str] = set()
    entries: list[str] = []
    warnings: list[str] = []
    for identifier in configured:
        if identifier in seen:
            warnings.append(
                f"WARNING: {identifier} appears multiple times in category "
                f"{category}; only the first occurrence will run."
            )
            continue
        seen.add(identifier)
        entries.append(identifier)
    unavailable = [
        identifier for identifier in entries if identifier not in catalog.tools
    ]
    if unavailable and not arguments.ignore_unavailable:
        for identifier in unavailable:
            print(f"ERROR: Enabled tool is unavailable: {identifier}", file=sys.stderr)
        print("Use --ignore-unavailable to skip unavailable tools.", file=sys.stderr)
        return 2
    for identifier in unavailable:
        warnings.append(f"WARNING: Skipping unavailable tool: {identifier}")

    log_lines = [f"category={category} operation={operation}"]
    log_lines.extend(warnings)
    for warning in warnings:
        print(warning)
    failed = False
    for identifier in entries:
        tool = catalog.tools.get(identifier)
        if tool is None:
            continue
        operation_data = tool.operations.get(operation)
        if operation_data is None:
            message = f"SKIP  {identifier:<36} no {operation} operation"
            print(message)
            log_lines.append(message)
            continue
        with tempfile.TemporaryDirectory(prefix="agent-tool-result-") as temporary:
            result_file = Path(temporary) / "result.json"
            environment = os.environ.copy()
            environment["AGENT_FRAMEWORK_RESULT_FILE"] = str(result_file)
            tools_path = str(Path(__file__).resolve().parent)
            old_pythonpath = environment.get("PYTHONPATH")
            environment["PYTHONPATH"] = (
                tools_path
                if not old_pythonpath
                else tools_path + os.pathsep + old_pythonpath
            )
            result = capture(
                [
                    sys.executable,
                    str(operation_data.script),
                    *operation_data.arguments,
                ],
                cwd=root,
                environment=environment,
            )
            status, reason = _result(result_file, result.returncode)
        if result.returncode and status != "skip":
            status = "fail"
        label = status.upper()
        suffix = f"  {reason}" if reason else ""
        message = f"{label:<5} {identifier:<36} {result.duration:.1f}s{suffix}"
        print(message)
        log_lines.extend(("", message, result.output.rstrip()))
        if (arguments.verbose or arguments._emit_full_output) and result.output:
            print(result.output, end="" if result.output.endswith("\n") else "\n")
        if status == "fail":
            failed = True
            if not arguments.verbose and not arguments._emit_full_output:
                print("\nLast 40 log lines:")
                print_tail(result.output)
    log_path = (
        root / ".agent-framework" / "logs" / f"{operation}_{category}" / "latest.log"
    )
    try:
        write_latest(log_path, "\n".join(log_lines).rstrip() + "\n")
    except OSError as exc:
        print(f"WARNING: Could not write log {log_path}: {exc}")
    if failed:
        print(f"\nComplete log: {log_path.relative_to(root)}")
    return 1 if failed else 0


def main_for_category(category: str, operation: str, arguments: list[str]) -> int:
    """CLI adapter for a category entry point."""

    try:
        return run_category(category, operation, _parse(category, operation, arguments))
    except CatalogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
