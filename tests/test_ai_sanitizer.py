import sys
from pathlib import Path

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "repository" / "ai_sanitizer"))

from run_ai_sanitizer import milestone_reference_lines


@covers("AF-TOOL-003")
def test_direct_milestone_reference_patterns_are_reported():
    text = "\n".join(
        (
            "See " + "MS" + "12 for the original implementation.",
            "Milestone " + "13 changed this behavior.",
            "See " + "m014" + ".md for details.",
            "The current milestone is intentionally generic.",
        )
    )

    findings = milestone_reference_lines(text)

    assert [line_number for line_number, _ in findings] == [1, 2, 3]
