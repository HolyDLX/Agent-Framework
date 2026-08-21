import importlib.util
import sys
from pathlib import Path

import pytest

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "contracts" / "generate_traceability.py"
spec = importlib.util.spec_from_file_location("generate_traceability", MODULE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_requirement_parser_ignores_fenced_examples(tmp_path: Path) -> None:
    path = tmp_path / "sample.md"
    path.write_text(
        "# X\n\n"
        "```markdown\n"
        "**FAKE-X-001** — fake\n"
        "Type: `behavioral`\n"
        "```\n\n"
        "**REAL-X-001** — real\n"
        "Type: `structural`\n",
        encoding="utf-8",
    )

    requirements = mod.parse_contract(path)

    assert [item.requirement_id for item in requirements] == ["REAL-X-001"]
    assert requirements[0].requirement_type == "structural"


def test_evaluation_parser_reads_requirements_and_methods(tmp_path: Path) -> None:
    path = tmp_path / "sample.md"
    path.write_text(
        "# Evaluation\n\n"
        "## EA-REAL-X-001\n\n"
        "Requirements: `REAL-X-001`\n"
        "Method: `automated-test`, `inspection`\n"
        "Evidence: `planned`\n\n"
        "Verify the behavior and inspect the repository structure.\n",
        encoding="utf-8",
    )

    activities = mod.parse_evaluation_file(path)

    assert len(activities) == 1
    assert activities[0].activity_id == "EA-REAL-X-001"
    assert activities[0].requirement_ids == ("REAL-X-001",)
    assert activities[0].methods == ("automated-test", "inspection")
    assert activities[0].evidence_state == "planned"


@covers("AF-TOOL-004")
def test_planned_automated_evidence_does_not_require_test_evidence(
    tmp_path: Path,
) -> None:
    contract = tmp_path / "contract.md"
    contract.write_text(
        "# Contract\n\n"
        "**REAL-X-001** — behavior will be implemented later.\n"
        "Type: `behavioral`\n",
        encoding="utf-8",
    )
    evaluation = tmp_path / "evaluation.md"
    evaluation.write_text(
        "# Evaluation\n\n"
        "## EA-REAL-X-001\n\n"
        "Requirements: `REAL-X-001`\n"
        "Method: `automated-test`\n"
        "Evidence: `planned`\n\n"
        "Add executable evidence with the implementation milestone.\n",
        encoding="utf-8",
    )

    requirements = mod.parse_contract(contract)
    activities = mod.parse_evaluation_file(evaluation)

    mod.validate_traceability(requirements, activities, [])
    assert mod._evaluation_status(activities, []) == "PLANNED-AUTOMATED"


def test_unplanned_automated_evidence_still_requires_covers(
    tmp_path: Path,
) -> None:
    contract = tmp_path / "contract.md"
    contract.write_text(
        "# Contract\n\n"
        "**REAL-X-001** — behavior is required now.\n"
        "Type: `behavioral`\n",
        encoding="utf-8",
    )
    evaluation = tmp_path / "evaluation.md"
    evaluation.write_text(
        "# Evaluation\n\n"
        "## EA-REAL-X-001\n\n"
        "Requirements: `REAL-X-001`\n"
        "Method: `automated-test`\n",
        encoding="utf-8",
    )

    requirements = mod.parse_contract(contract)
    activities = mod.parse_evaluation_file(evaluation)

    with pytest.raises(mod.TraceabilityError, match="missing @covers evidence"):
        mod.validate_traceability(requirements, activities, [])


def test_planned_evidence_requires_automated_test_method(tmp_path: Path) -> None:
    evaluation = tmp_path / "evaluation.md"
    evaluation.write_text(
        "# Evaluation\n\n"
        "## EA-REAL-X-001\n\n"
        "Requirements: `REAL-X-001`\n"
        "Method: `inspection`\n"
        "Evidence: `planned`\n",
        encoding="utf-8",
    )

    with pytest.raises(mod.TraceabilityError, match="without an automated-test method"):
        mod.parse_evaluation_file(evaluation)


def test_manual_evaluation_does_not_require_test_evidence(tmp_path: Path) -> None:
    contract = tmp_path / "contract.md"
    contract.write_text(
        "# Contract\n\n"
        "**REAL-X-001** — repository shape is constrained.\n"
        "Type: `structural`\n",
        encoding="utf-8",
    )
    evaluation = tmp_path / "evaluation.md"
    evaluation.write_text(
        "# Evaluation\n\n"
        "## EA-REAL-X-001\n\n"
        "Requirements: `REAL-X-001`\n"
        "Method: `inspection`\n\n"
        "Inspect the repository.\n",
        encoding="utf-8",
    )

    requirements = mod.parse_contract(contract)
    activities = mod.parse_evaluation_file(evaluation)

    mod.validate_traceability(requirements, activities, [])
    assert mod._evaluation_status(activities, []) == "MANUAL-REVIEW"
