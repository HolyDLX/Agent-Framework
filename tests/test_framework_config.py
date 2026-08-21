import sys
from pathlib import Path

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from _framework import black_target_version, load_config, project_image_name


@covers("AF-TOOL-001")
def test_framework_config_loads_own_project():
    config = load_config(ROOT)
    assert config.name == "agent-framework"
    assert config.source_paths == ("configure.py", "tools")
    assert config.coverage_exclude_paths == (
        "tools/run_actionlint.py",
        "tools/run_black.py",
        "tools/run_contracts.py",
        "tools/run_coverage.py",
        "tools/run_pydoclint.py",
        "tools/run_pyright.py",
        "tools/run_pytest.py",
        "tools/run_ruff.py",
        "tools/run_shellcheck.py",
        "tools/run_linkcheck.py",
        "tools/run_markdownlint.py",
        "tools/run_verification.py",
        "tools/run_yamllint.py",
    )
    assert project_image_name(config) == "agent-agent-framework-development"
    assert black_target_version(config) == "py312"
