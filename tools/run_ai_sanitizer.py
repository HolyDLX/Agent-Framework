"""Sanitize suspicious text and flag possible non-planning milestone references."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Protocol, TextIO, runtime_checkable

from _framework import load_config, project_root
from _tool_runner import run_custom_tool


@runtime_checkable
class _ReconfigurableTextIO(Protocol):
    """Text stream that supports runtime encoding reconfiguration."""

    def reconfigure(self, *, encoding: str | None = None) -> None:
        """Reconfigure the text encoding."""


def _configure_utf8(stream: TextIO) -> None:
    """Use UTF-8 output when the stream supports reconfiguration."""
    if isinstance(stream, _ReconfigurableTextIO):
        stream.reconfigure(encoding="utf-8")


_configure_utf8(sys.stdout)
_configure_utf8(sys.stderr)


PROJECT_ROOT = project_root()
_cfg = load_config(PROJECT_ROOT)
SCAN_ROOTS = (*_cfg.source_paths, *_cfg.test_paths, _cfg.docs_path, _cfg.readme)

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".json",
    ".yaml",
    ".toml",
    ".rst",
    ".cfg",
    ".ini",
    ".txt",
    ".yml",
}

IGNORED_PARTS = {
    ".git",
    ".venv",
    "agent-framework",
    "__pycache__",
    "_build",
    "coverage",
    "htmlcov",
}

# Never modify this sanitizer.
SELF = Path(__file__).resolve()


# Legitimate Unicode used in source code and technical documentation.
ALLOWED_UNICODE = {
    # Documentation arrows
    "\u2190",  # ←
    "\u2191",  # ↑
    "\u2192",  # →
    "\u2193",  # ↓
    "\u2194",  # ↔
    "\u21d0",  # ⇐
    "\u21d1",  # ⇑
    "\u21d2",  # ⇒
    "\u21d3",  # ⇓
    "\u21d4",  # ⇔
    # Mathematical symbols
    "\u00b1",  # ±
    "\u00d7",  # ×
    "\u00f7",  # ÷
    "\u2260",  # ≠
    "\u2264",  # ≤
    "\u2265",  # ≥
    "\u2248",  # ≈
    "\u221e",  # ∞
    "\u2212",  # −
    "\u2014",  # — required by contract declarations
    # Common technical symbols
    "\u2713",  # ✓
    "\u2714",  # ✔
    "\u2717",  # ✗
    "\u2718",  # ✘
}

# Preserve Unicode box-drawing characters used in Markdown diagrams.
ALLOWED_UNICODE.update(chr(codepoint) for codepoint in range(0x2500, 0x2580))


REPLACEMENTS = {
    # Quotes
    "\u2018": "'",
    "\u2019": "'",
    "\u201a": "'",
    "\u201b": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u201e": '"',
    "\u201f": '"',
    # Dashes
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2015": "-",
    # Spaces
    "\u00a0": " ",
    "\u2000": " ",
    "\u2001": " ",
    "\u2002": " ",
    "\u2003": " ",
    "\u2004": " ",
    "\u2005": " ",
    "\u2006": " ",
    "\u2007": " ",
    "\u2008": " ",
    "\u2009": " ",
    "\u200a": " ",
    "\u202f": " ",
    "\u205f": " ",
    "\u3000": " ",
    # Common punctuation
    "\u2026": "...",
    "\u00ab": '"',
    "\u00bb": '"',
    "\u2039": "'",
    "\u203a": "'",
    "\u2032": "'",
    "\u2033": '"',
    # Middle dot
    "\u00b7": ".",
}


# Characters commonly produced by UTF-8 -> CP1252 mojibake.
MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "â",
    "ð",
    "Ð",
    "ƒ",
)


# Advisory heuristic: direct milestone identities should remain planning-local.
MILESTONE_REFERENCE_PATTERNS = (
    re.compile(r"\bMS\d+(?:\.\d+)*\b", re.IGNORECASE),
    re.compile(r"\bmilestone\s+(?:MS\s*)?\d+(?:\.\d+)*\b", re.IGNORECASE),
    re.compile(
        r"\bm\d{3}(?:-(?:notes|handover|review))?\.md\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"docs[\\/]planning[\\/]milestones[\\/]m\d{3}"
        r"(?:-(?:notes|handover|review))?\.md\b",
        re.IGNORECASE,
    ),
)


def iter_files(scan_roots: tuple[str, ...] = SCAN_ROOTS) -> list[Path]:
    """Return text files files to scan."""

    files: list[Path] = []

    for root_name in scan_roots:
        root = PROJECT_ROOT / root_name

        if root.is_file():
            if root.resolve() != SELF and root.suffix.lower() in TEXT_SUFFIXES:
                files.append(root)

            continue

        if not root.exists():
            continue

        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.resolve() != SELF
            and path.suffix.lower() in TEXT_SUFFIXES
            and not any(part in IGNORED_PARTS for part in path.parts)
        )

    return sorted(files)


def _is_planning_document(path: Path) -> bool:
    """Return whether a scanned file belongs to project planning documentation."""
    try:
        relative = path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return False

    planning_root = Path(_cfg.docs_path) / "planning"
    try:
        relative.relative_to(planning_root)
    except ValueError:
        return False
    return True


def milestone_reference_lines(text: str) -> list[tuple[int, str]]:
    """Return lines containing possible direct milestone references."""
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in MILESTONE_REFERENCE_PATTERNS):
            findings.append((line_number, line.strip()))
    return findings


def milestone_reference_findings(path: Path, text: str) -> list[tuple[int, str]]:
    """Return advisory milestone-reference findings outside planning docs."""
    if _is_planning_document(path):
        return []
    return milestone_reference_lines(text)


def mojibake_score(text: str) -> int:
    """Estimate whether text contains UTF-8 mojibake."""

    return sum(text.count(marker) for marker in MOJIBAKE_MARKERS)


def encode_cp1252_for_repair(text: str) -> bytes:
    """Encode text as CP1252 while preserving C1 control characters."""

    result = bytearray()

    for character in text:
        codepoint = ord(character)

        if 0x80 <= codepoint <= 0x9F:
            result.append(codepoint)
        else:
            result.extend(character.encode("cp1252"))

    return bytes(result)


def repair_mojibake(text: str) -> str:
    """Repair repeated UTF-8/CP1252 encoding corruption."""

    current = text

    for _ in range(5):
        try:
            candidate = encode_cp1252_for_repair(current).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break

        if candidate == current:
            break

        before = mojibake_score(current)
        after = mojibake_score(candidate)

        if before == 0 or after >= before:
            break

        current = candidate

    return current


def is_suspicious(character: str) -> bool:
    """Return whether a character should be normalized."""

    if character in ALLOWED_UNICODE:
        return False

    if character in "\t\n\r":
        return False

    category = unicodedata.category(character)

    if category in {"Cc", "Cf", "Cs", "Co", "Cn"}:
        return True

    if character.isspace() and character != " ":
        return True

    return ord(character) > 127 and category[0] in {"P", "S"}


def replacement_for(character: str) -> str:
    """Return a safe replacement."""

    replacement = REPLACEMENTS.get(character)

    if replacement is not None:
        return replacement

    category = unicodedata.category(character)

    if character.isspace():
        return " "

    if category in {"Cc", "Cf", "Cs", "Co", "Cn"}:
        return ""

    normalized = unicodedata.normalize("NFKD", character)

    return normalized.encode("ascii", "ignore").decode("ascii")


def sanitize_unicode(text: str) -> tuple[str, int]:
    """Normalize suspicious Unicode characters and count findings."""

    result: list[str] = []
    findings = 0

    for character in text:
        if is_suspicious(character):
            result.append(replacement_for(character))
            findings += 1
        else:
            result.append(character)

    return "".join(result), findings


def changed_line_numbers(
    original: str,
    fixed: str,
) -> list[int]:
    """Return line numbers whose contents changed."""

    original_lines = original.splitlines()
    fixed_lines = fixed.splitlines()

    max_lines = max(len(original_lines), len(fixed_lines))
    result: list[int] = []

    for index in range(max_lines):
        old = original_lines[index] if index < len(original_lines) else ""
        new = fixed_lines[index] if index < len(fixed_lines) else ""

        if old != new:
            result.append(index + 1)

    return result


def describe_change(
    path: Path,
    original: str,
    fixed: str,
    show_changes: bool,
    show_locations: bool,
) -> None:
    """Print locations and/or changed lines."""

    lines = changed_line_numbers(original, fixed)

    if not lines:
        return

    relative = path.relative_to(PROJECT_ROOT)

    if show_locations:
        for line_number in lines:
            print(f"{relative}:{line_number}")

    if show_changes:
        original_lines = original.splitlines()
        fixed_lines = fixed.splitlines()

        max_lines = max(len(original_lines), len(fixed_lines))

        for index in range(max_lines):
            old = original_lines[index] if index < len(original_lines) else ""
            new = fixed_lines[index] if index < len(fixed_lines) else ""

            if old == new:
                continue

            print(f"FIX {relative}:{index + 1}")
            print(f"- {old}")
            print(f"+ {new}")


def scan(
    path: Path,
    fix: bool,
    show_changes: bool,
    show_locations: bool,
) -> tuple[int, bool]:
    """Scan and optionally repair one file."""

    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"WARNING {path}: not valid UTF-8 text")
        return 1, False

    # First repair encoding corruption.
    repaired = repair_mojibake(original)

    # Count suspicious Unicode after mojibake repair.
    fixed, unicode_findings = sanitize_unicode(repaired)

    mojibake_changed = repaired != original
    file_changed = fixed != original

    # A mojibake repair is one finding, regardless of how many
    # encoding-repair passes were required.
    findings = unicode_findings + int(mojibake_changed)

    if file_changed:
        describe_change(
            path,
            original,
            fixed,
            show_changes=show_changes,
            show_locations=show_locations,
        )

        if fix:
            path.write_text(fixed, encoding="utf-8")

    return findings, file_changed


def _run_local(arguments: list[str]) -> int:
    """Scan project files and optionally repair them locally."""
    parser = argparse.ArgumentParser(
        description="Sanitize suspicious text and review direct milestone references."
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="actually modify files",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="return failure status when findings exist",
    )

    parser.add_argument(
        "--changes",
        action="store_true",
        help="show the changed lines",
    )

    parser.add_argument(
        "--locations",
        action="store_true",
        help="show only file paths and line numbers",
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="relative files or directories to scan; defaults to the project",
    )

    args = parser.parse_args(arguments)

    total_findings = 0
    affected_files = 0
    milestone_findings: list[tuple[Path, int, str]] = []

    scan_roots = tuple(args.paths) or SCAN_ROOTS
    for path in iter_files(scan_roots):
        findings, file_changed = scan(
            path,
            fix=args.fix,
            show_changes=args.changes,
            show_locations=args.locations,
        )

        total_findings += findings

        if file_changed:
            affected_files += 1

        try:
            current_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in milestone_reference_findings(path, current_text):
            milestone_findings.append((path, line_number, line))

    if args.fix:
        print(
            f"AI sanitizer: found {total_findings} issue(s), "
            f"fixed {total_findings} issue(s) "
            f"in {affected_files} file(s)"
        )
    else:
        print(
            f"AI sanitizer: found {total_findings} issue(s), "
            f"would fix {total_findings} issue(s) "
            f"in {affected_files} file(s)"
        )

    if milestone_findings:
        print()
        print(
            "Milestone reference review: "
            f"{len(milestone_findings)} possible direct reference(s) found "
            "outside planning documentation."
        )
        for path, line_number, line in milestone_findings:
            relative = path.relative_to(PROJECT_ROOT)
            excerpt = f": {line}" if line else ""
            print(f"REVIEW {relative}:{line_number}{excerpt}")
        print(
            "Go review these files/lines and determine whether they reference "
            "project milestones directly. Direct milestone references should "
            "exist only under docs/planning/. These findings are advisory and "
            "do not change the sanitizer exit status."
        )
    else:
        print(
            "Milestone reference review: no possible direct milestone "
            "references found outside planning documentation."
        )

    return int(args.strict and total_findings > 0)


def main() -> int:
    """Scan project files and optionally repair them."""
    return run_custom_tool(Path(__file__), _run_local, ())


if __name__ == "__main__":
    raise SystemExit(main())
