"""Run the opinionated Agent Framework verification groups."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _framework import FRAMEWORK_ROOT, project_root
from _tool_runner import run_custom_tool

GROUPS = {
    "code": (
        ("run_black.py", ()),
        ("run_ruff.py", ()),
        ("run_pydoclint.py", ()),
        ("run_pyright.py", ()),
        ("run_ai_sanitizer.py", ("--strict",)),
    ),
    "docs": (
        ("run_markdownlint.py", ()),
        ("run_linkcheck.py", ()),
    ),
    "testing": (
        ("run_pytest.py", ()),
        ("run_coverage.py", ()),
    ),
    "contracts": (("run_contracts.py", ()),),
    "repository": (
        ("run_shellcheck.py", ()),
        ("run_yamllint.py", ()),
        ("run_actionlint.py", ()),
    ),
}


FIXERS = {
    "code": (
        ("run_ai_sanitizer.py", ("--fix",)),
        ("run_ruff.py", ("--fix",)),
        ("run_black.py", ("--fix",)),
    ),
    "docs": (("run_markdownlint.py", ("--fix",)),),
    "contracts": (("run_contracts.py", ("--fix",)),),
}


def _parse(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="apply supported automatic fixes before verification",
    )
    parser.add_argument(
        "groups",
        nargs="*",
        choices=tuple(GROUPS),
    )
    return parser.parse_args(arguments)


def _run_runner(
    root: Path,
    runner: str,
    arguments: tuple[str, ...],
) -> int:
    return subprocess.run(
        [
            sys.executable,
            str(FRAMEWORK_ROOT / "tools" / runner),
            *arguments,
        ],
        cwd=root,
        check=False,
    ).returncode


def _local(arguments: list[str]) -> int:
    parsed = _parse(arguments)
    root = project_root()
    groups = parsed.groups or list(GROUPS)

    if parsed.fix:
        for group in groups:
            fixers = FIXERS.get(group, ())

            if not fixers:
                continue

            print(f"== fix: {group} ==")

            for runner, runner_arguments in fixers:
                result = _run_runner(
                    root,
                    runner,
                    runner_arguments,
                )

                if result:
                    return result

    # Always run normal verification after fixing.
    for group in groups:
        print(f"== {group} ==")

        for runner, runner_arguments in GROUPS[group]:
            result = _run_runner(
                root,
                runner,
                runner_arguments,
            )

            if result:
                return result

    return 0


def main() -> int:
    """Apply optional fixes and run verification."""
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
