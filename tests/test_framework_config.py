import sys
from pathlib import Path

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from _framework import (
    black_target_version,
    has_project_tool_config,
    load_config,
    project_image_name,
)


@covers("AF-TOOL-001")
def test_framework_config_loads_own_project():
    config = load_config(ROOT)
    assert config.name == "agent-framework"
    assert config.source_paths == ("configure.py", "toolctl.py", "tools")
    assert config.coverage_exclude_paths == (
        "tools/ci/actionlint/run_actionlint.py",
        "tools/code/black/run_black.py",
        "tools/code/pydoclint/run_pydoclint.py",
        "tools/code/pyright/run_pyright.py",
        "tools/code/ruff/run_ruff.py",
        "tools/configuration/yamllint/run_yamllint.py",
        "tools/contracts/traceability/run_contracts.py",
        "tools/documentation/linkcheck/run_linkcheck.py",
        "tools/documentation/markdownlint/run_markdownlint.py",
        "tools/repository/ai_sanitizer/run_ai_sanitizer.py",
        "tools/shell/shellcheck/run_shellcheck.py",
        "tools/tests/coverage/run_coverage.py",
        "tools/tests/pytest/run_pytest.py",
        "tools/ci/fix_ci.py",
        "tools/ci/verify_ci.py",
        "tools/code/fix_code.py",
        "tools/code/verify_code.py",
        "tools/configuration/fix_configuration.py",
        "tools/configuration/verify_configuration.py",
        "tools/contracts/fix_contracts.py",
        "tools/contracts/verify_contracts.py",
        "tools/documentation/fix_documentation.py",
        "tools/documentation/verify_documentation.py",
        "tools/repository/fix_repository.py",
        "tools/repository/verify_repository.py",
        "tools/shell/fix_shell.py",
        "tools/shell/verify_shell.py",
        "tools/tests/fix_tests.py",
        "tools/tests/verify_tests.py",
        "tools/run_verification.py",
    )
    assert project_image_name(config) == "agent-agent-framework-development"
    assert black_target_version(config) == "py312"


@covers("AF-TOOL-001", "AF-TOOL-002")
def test_project_tool_configuration_is_detected(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[tool.black]\nline-length = 100\n\n[tool.ruff.lint]\nselect = ['E']\n",
        encoding="utf-8",
    )

    assert has_project_tool_config("black", tmp_path)
    assert has_project_tool_config("ruff", tmp_path)
    assert not has_project_tool_config("pyright", tmp_path)
