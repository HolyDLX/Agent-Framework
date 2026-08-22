"""Generate requirement and evaluation-aware traceability CSV files.

Requirement syntax
==================

A normative requirement is a normal Markdown paragraph beginning with a stable
ID in bold followed by an em dash. The final line declares its requirement type:

    **SET-PRE-012** - Any exception raised by a pre-commit hook aborts the
    transaction and leaves the committed configuration unchanged.
    Type: `behavioral`

Supported requirement types are ``behavioral``, ``structural``, and ``process``.
Requirement type describes the obligation; it does not prescribe how the
obligation is evaluated.

Evaluation activity syntax
==========================

Evaluation activities live in ``docs/contracts/evaluation/*.md`` and use a
stable heading plus requirement and method declarations:

    ## EA-SET-PRE-012

    Requirements: `SET-PRE-012`
    Method: `automated-test`, `inspection`
    Evidence: `planned`

Supported methods are ``automated-test``, ``inspection``, and ``analysis``. The
optional ``Evidence: `planned``` declaration is valid only for activities
that include ``automated-test`` and explicitly allows executable evidence to be
deferred. Without that marker, an automated-test method requires matching
executable coverage evidence now. Inspection- and analysis-only requirements
remain valid manual review items.

Test coverage syntax
====================

Tests declare automated evidence with literal requirement IDs:

    @covers("SET-PRE-012")
    def test_pre_commit_failure_aborts_transaction():
        ...

The generator parses Python with ``ast``. Test modules are never imported or
executed.

Outputs
=======

By default:

    docs/contracts/generated/requirements.csv
    docs/contracts/generated/traceability.csv

Use ``--check`` to verify that committed/generated CSVs are current without
rewriting them. The command also fails for duplicate or malformed requirement
or evaluation declarations, unknown IDs, missing evaluation activities,
automated-test activities without executable evidence unless that evidence is
explicitly planned, or ``@covers(...)`` claims for requirements that define no
automated-test evaluation method.
"""

from __future__ import annotations

import argparse
import ast
import csv
import io
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REQUIREMENT_START_RE = re.compile(
    r"^\*\*(?P<id>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+-\d{3})\*\*\s+-\s+(?P<text>.+?)\s*$"
)
REQUIREMENT_TYPE_RE = re.compile(r"^Type:\s+`(?P<type>[a-z-]+)`\s*$")
LOOKS_LIKE_REQUIREMENT_RE = re.compile(r"^\*\*([A-Z][A-Z0-9-]*-\d+)\*\*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
EVALUATION_HEADING_RE = re.compile(r"^##\s+(?P<id>EA-[A-Z][A-Z0-9-]+-\d{3})\s*$")
EVALUATION_REQUIREMENTS_RE = re.compile(r"^Requirements:\s+(?P<value>.+?)\s*$")
EVALUATION_METHOD_RE = re.compile(r"^Method:\s+(?P<value>.+?)\s*$")
EVALUATION_EVIDENCE_RE = re.compile(r"^Evidence:\s+(?P<value>.+?)\s*$")
BACKTICK_VALUE_RE = re.compile(r"`([^`]+)`")

REQUIREMENT_TYPES = frozenset({"behavioral", "structural", "process"})
EVALUATION_METHODS = frozenset({"automated-test", "inspection", "analysis"})
EVALUATION_EVIDENCE_STATES = frozenset({"planned"})
MANUAL_METHODS = frozenset({"inspection", "analysis"})


@dataclass(frozen=True)
class Requirement:
    contract: str
    requirement_id: str
    requirement_type: str
    section: str
    text: str
    source_line: int


@dataclass(frozen=True)
class EvaluationActivity:
    activity_id: str
    evaluation_file: str
    requirement_ids: tuple[str, ...]
    methods: tuple[str, ...]
    evidence_state: str | None
    source_line: int


@dataclass(frozen=True)
class Coverage:
    requirement_id: str
    test_file: str
    test_name: str
    source_line: int


class TraceabilityError(Exception):
    """Raised for malformed or inconsistent traceability declarations."""


def iter_markdown_files(contracts_dir: Path) -> Iterable[Path]:
    """Yield authoritative contract Markdown files."""
    for path in sorted(contracts_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        yield path


def iter_evaluation_files(evaluation_dir: Path) -> Iterable[Path]:
    """Yield evaluation activity Markdown files."""
    for path in sorted(evaluation_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        yield path


def _section_name(headings: dict[int, str]) -> str:
    if not headings:
        return ""
    return " > ".join(headings[level] for level in sorted(headings))


def parse_contract(path: Path) -> list[Requirement]:
    """Parse typed normative requirements from one contract document."""
    lines = path.read_text(encoding="utf-8").splitlines()
    requirements: list[Requirement] = []
    headings: dict[int, str] = {}
    i = 0
    in_fence = False

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue

        if in_fence:
            i += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = heading.group(2).strip()
            i += 1
            continue

        match = REQUIREMENT_START_RE.match(line)
        if match:
            start_line = i + 1
            requirement_id = match.group("id")
            parts = [match.group("text").strip()]
            i += 1
            requirement_type: str | None = None

            while i < len(lines) and lines[i].strip():
                type_match = REQUIREMENT_TYPE_RE.match(lines[i])
                if type_match:
                    requirement_type = type_match.group("type")
                    i += 1
                    if i < len(lines) and lines[i].strip():
                        raise TraceabilityError(
                            f"{path}:{i + 1}: requirement metadata must be the "
                            "final non-blank line of the declaration"
                        )
                    break

                if HEADING_RE.match(lines[i]) or REQUIREMENT_START_RE.match(lines[i]):
                    break
                parts.append(lines[i].strip())
                i += 1

            if requirement_type is None:
                raise TraceabilityError(
                    f"{path}:{start_line}: {requirement_id} is missing "
                    "'Type: `behavioral|structural|process`'"
                )
            if requirement_type not in REQUIREMENT_TYPES:
                supported = ", ".join(sorted(REQUIREMENT_TYPES))
                raise TraceabilityError(
                    f"{path}:{start_line}: {requirement_id} has unsupported type "
                    f"{requirement_type!r}; expected one of {supported}"
                )

            requirements.append(
                Requirement(
                    contract=path.name,
                    requirement_id=requirement_id,
                    requirement_type=requirement_type,
                    section=_section_name(headings),
                    text=" ".join(parts),
                    source_line=start_line,
                )
            )
            continue

        suspicious = LOOKS_LIKE_REQUIREMENT_RE.match(line)
        if suspicious:
            raise TraceabilityError(
                f"{path}:{i + 1}: requirement-like declaration does not use "
                f"the required '**ID** - text' form"
            )

        i += 1

    return requirements


def _backtick_values(
    path: Path, line_number: int, label: str, value: str
) -> tuple[str, ...]:
    values = tuple(BACKTICK_VALUE_RE.findall(value))
    if not values:
        raise TraceabilityError(
            f"{path}:{line_number}: {label} must contain one or more backtick values"
        )
    return values


def parse_evaluation_file(path: Path) -> list[EvaluationActivity]:
    """Parse evaluation activities from one Markdown document."""
    lines = path.read_text(encoding="utf-8").splitlines()
    activities: list[EvaluationActivity] = []
    i = 0
    in_fence = False

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        heading = EVALUATION_HEADING_RE.match(line)
        if heading is None:
            i += 1
            continue

        activity_id = heading.group("id")
        source_line = i + 1
        requirement_ids: tuple[str, ...] | None = None
        methods: tuple[str, ...] | None = None
        evidence_state: str | None = None
        i += 1

        while i < len(lines):
            next_heading = HEADING_RE.match(lines[i])
            if next_heading and len(next_heading.group(1)) <= 2:
                break

            requirements_match = EVALUATION_REQUIREMENTS_RE.match(lines[i])
            if requirements_match:
                if requirement_ids is not None:
                    raise TraceabilityError(
                        f"{path}:{i + 1}: duplicate Requirements declaration "
                        f"for {activity_id}"
                    )
                requirement_ids = _backtick_values(
                    path, i + 1, "Requirements", requirements_match.group("value")
                )

            method_match = EVALUATION_METHOD_RE.match(lines[i])
            if method_match:
                if methods is not None:
                    raise TraceabilityError(
                        f"{path}:{i + 1}: duplicate Method declaration for {activity_id}"
                    )
                methods = _backtick_values(
                    path, i + 1, "Method", method_match.group("value")
                )

            evidence_match = EVALUATION_EVIDENCE_RE.match(lines[i])
            if evidence_match:
                if evidence_state is not None:
                    raise TraceabilityError(
                        f"{path}:{i + 1}: duplicate Evidence declaration "
                        f"for {activity_id}"
                    )
                evidence_values = _backtick_values(
                    path, i + 1, "Evidence", evidence_match.group("value")
                )
                if len(evidence_values) != 1:
                    raise TraceabilityError(
                        f"{path}:{i + 1}: Evidence must contain exactly one "
                        "backtick value"
                    )
                evidence_state = evidence_values[0]
            i += 1

        if requirement_ids is None:
            raise TraceabilityError(
                f"{path}:{source_line}: {activity_id} is missing Requirements"
            )
        if methods is None:
            raise TraceabilityError(
                f"{path}:{source_line}: {activity_id} is missing Method"
            )
        invalid_methods = sorted(set(methods) - EVALUATION_METHODS)
        if invalid_methods:
            raise TraceabilityError(
                f"{path}:{source_line}: {activity_id} uses unsupported evaluation "
                f"method(s): {', '.join(invalid_methods)}"
            )
        if (
            evidence_state is not None
            and evidence_state not in EVALUATION_EVIDENCE_STATES
        ):
            supported = ", ".join(sorted(EVALUATION_EVIDENCE_STATES))
            raise TraceabilityError(
                f"{path}:{source_line}: {activity_id} uses unsupported Evidence "
                f"state {evidence_state!r}; expected one of {supported}"
            )
        if evidence_state == "planned" and "automated-test" not in methods:
            raise TraceabilityError(
                f"{path}:{source_line}: {activity_id} declares planned evidence "
                "without an automated-test method"
            )

        activities.append(
            EvaluationActivity(
                activity_id=activity_id,
                evaluation_file=path.name,
                requirement_ids=requirement_ids,
                methods=methods,
                evidence_state=evidence_state,
                source_line=source_line,
            )
        )

    return activities


def _decorator_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


class CoverageVisitor(ast.NodeVisitor):
    """Collect literal ``@covers`` declarations from test functions."""

    def __init__(self, path: Path, display_path: str):
        self.path = path
        self.display_path = display_path
        self.class_stack: list[str] = []
        self.coverage: list[Coverage] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualified_name = ".".join((*self.class_stack, node.name))

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if _decorator_name(decorator.func) != "covers":
                continue

            if decorator.keywords:
                raise TraceabilityError(
                    f"{self.path}:{decorator.lineno}: @covers() accepts only "
                    "literal positional requirement IDs"
                )
            if not decorator.args:
                raise TraceabilityError(
                    f"{self.path}:{decorator.lineno}: @covers() has no IDs"
                )

            for argument in decorator.args:
                if not (
                    isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                    and argument.value
                ):
                    raise TraceabilityError(
                        f"{self.path}:{getattr(argument, 'lineno', decorator.lineno)}: "
                        "@covers() IDs must be string literals"
                    )

                self.coverage.append(
                    Coverage(
                        requirement_id=argument.value,
                        test_file=self.display_path,
                        test_name=qualified_name,
                        source_line=node.lineno,
                    )
                )

        self.generic_visit(node)


def parse_test_file(path: Path, display_path: str) -> list[Coverage]:
    """Parse coverage declarations from one Python test module."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise TraceabilityError(f"cannot parse {path}: {exc}") from exc

    visitor = CoverageVisitor(path, display_path)
    visitor.visit(tree)
    return visitor.coverage


def iter_test_files(tests_dir: Path) -> Iterable[Path]:
    """Yield Python test files recursively."""
    for path in sorted(tests_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        yield path


def collect_requirements(contracts_dir: Path) -> list[Requirement]:
    """Collect requirements and reject duplicate IDs."""
    requirements: list[Requirement] = []
    seen: dict[str, Requirement] = {}

    for path in iter_markdown_files(contracts_dir):
        for requirement in parse_contract(path):
            previous = seen.get(requirement.requirement_id)
            if previous is not None:
                raise TraceabilityError(
                    "duplicate requirement ID "
                    f"{requirement.requirement_id}: "
                    f"{previous.contract}:{previous.source_line} and "
                    f"{requirement.contract}:{requirement.source_line}"
                )
            seen[requirement.requirement_id] = requirement
            requirements.append(requirement)

    return requirements


def collect_evaluations(evaluation_dir: Path) -> list[EvaluationActivity]:
    """Collect evaluation activities and reject duplicate activity IDs."""
    activities: list[EvaluationActivity] = []
    seen: dict[str, EvaluationActivity] = {}

    for path in iter_evaluation_files(evaluation_dir):
        for activity in parse_evaluation_file(path):
            previous = seen.get(activity.activity_id)
            if previous is not None:
                raise TraceabilityError(
                    "duplicate evaluation activity ID "
                    f"{activity.activity_id}: "
                    f"{previous.evaluation_file}:{previous.source_line} and "
                    f"{activity.evaluation_file}:{activity.source_line}"
                )
            seen[activity.activity_id] = activity
            activities.append(activity)

    return activities


def collect_coverage(tests_dir: Path, project_root: Path) -> list[Coverage]:
    """Collect executable coverage declarations."""
    coverage: list[Coverage] = []
    for path in iter_test_files(tests_dir):
        try:
            display = path.relative_to(project_root).as_posix()
        except ValueError:
            display = path.as_posix()
        coverage.extend(parse_test_file(path, display))
    return coverage


def _evaluations_by_requirement(
    activities: list[EvaluationActivity],
) -> dict[str, list[EvaluationActivity]]:
    result: dict[str, list[EvaluationActivity]] = {}
    for activity in activities:
        for requirement_id in activity.requirement_ids:
            result.setdefault(requirement_id, []).append(activity)
    return result


def _coverage_by_requirement(coverage: list[Coverage]) -> dict[str, list[Coverage]]:
    result: dict[str, list[Coverage]] = {}
    for item in coverage:
        result.setdefault(item.requirement_id, []).append(item)
    return result


def validate_traceability(
    requirements: list[Requirement],
    activities: list[EvaluationActivity],
    coverage: list[Coverage],
) -> None:
    """Validate requirement, evaluation, and automated-evidence consistency."""
    known = {requirement.requirement_id for requirement in requirements}
    unknown_evaluation_refs: dict[str, list[EvaluationActivity]] = {}
    for activity in activities:
        for requirement_id in activity.requirement_ids:
            if requirement_id not in known:
                unknown_evaluation_refs.setdefault(requirement_id, []).append(activity)

    if unknown_evaluation_refs:
        details: list[str] = []
        for requirement_id in sorted(unknown_evaluation_refs):
            locations = ", ".join(
                f"{item.evaluation_file}:{item.source_line}"
                for item in unknown_evaluation_refs[requirement_id]
            )
            details.append(f"{requirement_id} referenced by {locations}")
        raise TraceabilityError(
            "evaluation activities reference unknown requirement IDs:\n  "
            + "\n  ".join(details)
        )

    unknown_coverage: dict[str, list[Coverage]] = {}
    for item in coverage:
        if item.requirement_id not in known:
            unknown_coverage.setdefault(item.requirement_id, []).append(item)
    if unknown_coverage:
        details: list[str] = []
        for requirement_id in sorted(unknown_coverage):
            locations = ", ".join(
                f"{item.test_file}:{item.source_line}"
                for item in unknown_coverage[requirement_id]
            )
            details.append(f"{requirement_id} referenced by {locations}")
        raise TraceabilityError(
            "tests reference unknown contract requirement IDs:\n  "
            + "\n  ".join(details)
        )

    by_evaluation = _evaluations_by_requirement(activities)
    by_coverage = _coverage_by_requirement(coverage)
    missing_evaluation: list[str] = []
    missing_automated_evidence: list[str] = []
    automated_without_method: list[str] = []

    for requirement in requirements:
        requirement_id = requirement.requirement_id
        requirement_activities = by_evaluation.get(requirement_id, [])
        if not requirement_activities:
            missing_evaluation.append(requirement_id)
            continue

        methods = {
            method for activity in requirement_activities for method in activity.methods
        }
        automated_activities = [
            activity
            for activity in requirement_activities
            if "automated-test" in activity.methods
        ]
        has_tests = bool(by_coverage.get(requirement_id))
        automated_evidence_is_planned = bool(automated_activities) and all(
            activity.evidence_state == "planned" for activity in automated_activities
        )
        if (
            "automated-test" in methods
            and not has_tests
            and not automated_evidence_is_planned
        ):
            missing_automated_evidence.append(requirement_id)
        if has_tests and "automated-test" not in methods:
            automated_without_method.append(requirement_id)

    problems: list[str] = []
    if missing_evaluation:
        problems.append(
            "requirements missing evaluation activities: "
            + ", ".join(sorted(missing_evaluation))
        )
    if missing_automated_evidence:
        problems.append(
            "automated-test requirements missing @covers evidence: "
            + ", ".join(sorted(missing_automated_evidence))
        )
    if automated_without_method:
        problems.append(
            "requirements have @covers evidence but no automated-test evaluation method: "
            + ", ".join(sorted(automated_without_method))
        )
    if problems:
        raise TraceabilityError("\n".join(problems))


def _evaluation_status(
    activities: list[EvaluationActivity], coverage: list[Coverage]
) -> str:
    if not activities:
        return "MISSING-EVALUATION"
    methods = {method for activity in activities for method in activity.methods}
    has_automated = "automated-test" in methods
    has_manual = bool(methods & MANUAL_METHODS)
    has_tests = bool(coverage)
    automated_activities = [
        activity for activity in activities if "automated-test" in activity.methods
    ]
    automated_evidence_is_planned = bool(automated_activities) and all(
        activity.evidence_state == "planned" for activity in automated_activities
    )
    if has_automated and not has_tests and automated_evidence_is_planned:
        return "PLANNED-AUTOMATED"
    if has_automated and not has_tests:
        return "MISSING-AUTOMATED-EVIDENCE"
    if has_automated and has_manual:
        return "MIXED"
    if has_automated:
        return "AUTOMATED"
    return "MANUAL-REVIEW"


def render_requirements_csv(requirements: list[Requirement]) -> str:
    """Render the typed requirement inventory."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["contract", "id", "type", "section", "requirement", "source_line"])
    for requirement in sorted(
        requirements,
        key=lambda item: (item.contract, item.source_line, item.requirement_id),
    ):
        writer.writerow(
            [
                requirement.contract,
                requirement.requirement_id,
                requirement.requirement_type,
                requirement.section,
                requirement.text,
                requirement.source_line,
            ]
        )
    return output.getvalue()


def render_traceability_csv(
    requirements: list[Requirement],
    activities: list[EvaluationActivity],
    coverage: list[Coverage],
) -> str:
    """Render evaluation-aware requirement traceability."""
    evaluations = _evaluations_by_requirement(activities)
    by_coverage = _coverage_by_requirement(coverage)

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "contract",
            "id",
            "type",
            "section",
            "requirement",
            "evaluation_status",
            "evaluation_methods",
            "automated_evidence_state",
            "evaluation_activities",
            "test_count",
            "tests",
        ]
    )

    for requirement in sorted(
        requirements,
        key=lambda item: (item.contract, item.source_line, item.requirement_id),
    ):
        requirement_activities = sorted(
            evaluations.get(requirement.requirement_id, []),
            key=lambda item: (item.evaluation_file, item.source_line, item.activity_id),
        )
        items = sorted(
            by_coverage.get(requirement.requirement_id, []),
            key=lambda item: (item.test_file, item.test_name, item.source_line),
        )
        methods = sorted(
            {
                method
                for activity in requirement_activities
                for method in activity.methods
            }
        )
        tests = "; ".join(f"{item.test_file}::{item.test_name}" for item in items)
        automated_activities = [
            activity
            for activity in requirement_activities
            if "automated-test" in activity.methods
        ]
        evidence_states = sorted(
            {activity.evidence_state or "required" for activity in automated_activities}
        )
        activity_ids = "; ".join(item.activity_id for item in requirement_activities)
        writer.writerow(
            [
                requirement.contract,
                requirement.requirement_id,
                requirement.requirement_type,
                requirement.section,
                requirement.text,
                _evaluation_status(requirement_activities, items),
                "; ".join(methods),
                "; ".join(evidence_states),
                activity_ids,
                len(items),
                tests,
            ]
        )

    return output.getvalue()


def _check_file(path: Path, expected: str) -> bool:
    if not path.exists():
        print(f"STALE: missing {path}", file=sys.stderr)
        return False
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        print(f"STALE: {path}", file=sys.stderr)
        return False
    return True


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="project root; defaults to the current working directory",
    )
    parser.add_argument(
        "--contracts",
        type=Path,
        default=Path("docs/contracts"),
        help="contracts directory relative to project root",
    )
    parser.add_argument(
        "--evaluations",
        type=Path,
        default=Path("docs/contracts/evaluation"),
        help="evaluation activity directory relative to project root",
    )
    parser.add_argument(
        "--tests",
        type=Path,
        default=Path("tests"),
        help="tests directory relative to project root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/contracts/generated"),
        help="generated CSV directory relative to project root",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated files are current instead of writing them",
    )
    return parser


def resolve_under(root: Path, path: Path) -> Path:
    """Resolve a possibly relative path under the project root."""
    return path if path.is_absolute() else root / path


def _status_counts(
    requirements: list[Requirement],
    activities: list[EvaluationActivity],
    coverage: list[Coverage],
) -> dict[str, int]:
    evaluations = _evaluations_by_requirement(activities)
    by_coverage = _coverage_by_requirement(coverage)
    counts: dict[str, int] = {}
    for requirement in requirements:
        status = _evaluation_status(
            evaluations.get(requirement.requirement_id, []),
            by_coverage.get(requirement.requirement_id, []),
        )
        counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    """Generate or check evaluation-aware traceability artifacts."""
    args = build_parser().parse_args()
    project_root = args.project_root.resolve()
    contracts_dir = resolve_under(project_root, args.contracts)
    evaluation_dir = resolve_under(project_root, args.evaluations)
    tests_dir = resolve_under(project_root, args.tests)
    output_dir = resolve_under(project_root, args.output)

    try:
        requirements = collect_requirements(contracts_dir)
        activities = collect_evaluations(evaluation_dir)
        coverage = collect_coverage(tests_dir, project_root)
        validate_traceability(requirements, activities, coverage)
    except (OSError, TraceabilityError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    requirements_csv = render_requirements_csv(requirements)
    traceability_csv = render_traceability_csv(requirements, activities, coverage)

    requirements_path = output_dir / "requirements.csv"
    traceability_path = output_dir / "traceability.csv"

    if args.check:
        current = _check_file(requirements_path, requirements_csv) and _check_file(
            traceability_path, traceability_csv
        )
        if not current:
            return 1
    else:
        _write_file(requirements_path, requirements_csv)
        _write_file(traceability_path, traceability_csv)

    counts = _status_counts(requirements, activities, coverage)
    print(
        f"Requirements: {len(requirements)} | "
        f"automated: {counts.get('AUTOMATED', 0)} | "
        f"mixed: {counts.get('MIXED', 0)} | "
        f"manual review: {counts.get('MANUAL-REVIEW', 0)} | "
        f"planned automated: {counts.get('PLANNED-AUTOMATED', 0)} | "
        f"missing: {counts.get('MISSING-EVALUATION', 0) + counts.get('MISSING-AUTOMATED-EVIDENCE', 0)}"
    )
    print(
        f"Evaluation activities: {len(activities)} | "
        f"coverage declarations: {len(coverage)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
