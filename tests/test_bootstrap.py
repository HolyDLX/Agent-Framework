import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pytest import CaptureFixture, MonkeyPatch

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import configure


def _copy_framework(project: Path) -> Path:
    import shutil

    framework = project / "agent-framework"
    project.mkdir()
    shutil.copytree(
        ROOT,
        framework,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
    )
    return framework


def _framework_override(framework: Path) -> Callable[[], Path]:
    return lambda: framework


def _clean_submodule(*_arguments: Any) -> None:
    return None


@covers("AF-OWN-002")
def test_configure_rejects_conflicts_before_writing(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    project = tmp_path / "consumer"
    framework = _copy_framework(project)
    conflict = project / "README.md"
    conflict.write_text("sentinel\n", encoding="utf-8")
    monkeypatch.setattr(configure, "framework_root", _framework_override(framework))
    monkeypatch.setattr(configure, "_submodule_warning", _clean_submodule)

    with pytest.raises(RuntimeError, match="Unexpected root paths"):
        configure.configure("Consumer", "Example intent.", "3.12", "generic")

    assert conflict.read_text(encoding="utf-8") == "sentinel\n"
    assert not (project / "AGENTS.md").exists()


@covers(
    "AF-BOOT-005",
    "AF-BOOT-006",
    "AF-BOOT-008",
    "AF-BOOT-011",
    "AF-BOOT-012",
)
def test_configure_creates_deterministic_scaffold(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    project = tmp_path / "consumer"
    framework = _copy_framework(project)
    (project / ".git").mkdir()
    (project / ".gitmodules").write_text("submodule\n", encoding="utf-8")
    monkeypatch.setattr(configure, "framework_root", _framework_override(framework))
    monkeypatch.setattr(configure, "_submodule_warning", _clean_submodule)

    configure.configure("My Project", "Intent kept verbatim.", "3.14", "generic")

    assert 'name = "my-project"' in (project / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.14"' in (project / "pyproject.toml").read_text()
    assert "agent-framework-python:3.14-local" in (project / "Dockerfile").read_text()
    assert (project / "src" / "my_project" / "main.py").exists()
    assert (
        "from my_project.main import main"
        in (project / "tests" / "test_main.py").read_text()
    )
    assert "Intent kept verbatim." in (project / "README.md").read_text()
    assert (
        "Intent kept verbatim."
        in (project / "docs" / "architecture" / "README.md").read_text()
    )
    assert (
        "No implementation milestone"
        in (project / "docs" / "planning" / "roadmap.md").read_text()
    )
    configured = (project / "agent-framework.toml").read_text(encoding="utf-8")
    assert '"code/black"' in configured
    assert '"tests/coverage"' in configured
    assert '"tests/pytest"' not in configured
    assert (project / "toolctl.py").is_file()
    assert (project / "run_verification.py").is_file()


@covers("AF-BOOT-011")
def test_unknown_profile_fails_before_writes(tmp_path: Path, monkeypatch: MonkeyPatch):
    project = tmp_path / "consumer"
    framework = _copy_framework(project)
    (project / ".git").mkdir()
    (project / ".gitmodules").write_text("submodule\n", encoding="utf-8")
    monkeypatch.setattr(configure, "framework_root", _framework_override(framework))
    monkeypatch.setattr(configure, "_submodule_warning", _clean_submodule)

    with pytest.raises(ValueError, match="Unknown bootstrap profile"):
        configure.configure("Consumer", "Intent", "3.12", "missing")

    assert not (project / "README.md").exists()


@covers("AF-BOOT-007")
@pytest.mark.parametrize("name", ["123 Client", "class", "invalid.name"])
def test_configure_rejects_invalid_project_names(name: str):
    with pytest.raises(ValueError):
        configure.normalized_names(name)


@covers("AF-BOOT-011")
def test_configuration_defaults_to_python_312(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["configure.py", "--project-name", "Consumer", "--intent", "Intent"],
    )

    with pytest.raises(SystemExit):
        configure.parse_arguments()


@covers("AF-BOOT-008", "AF-BOOT-011")
def test_configuration_defaults_to_python_312_with_explicit_profile(
    monkeypatch: MonkeyPatch,
):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "configure.py",
            "--project-name",
            "Consumer",
            "--intent",
            "Intent",
            "--profile",
            "generic",
        ],
    )

    arguments = configure.parse_arguments()

    assert arguments.python_version == "3.12"


@covers("AF-BOOT-010")
def test_configure_preserves_and_warns_about_ignored_paths(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
):
    project = tmp_path / "consumer"
    framework = _copy_framework(project)
    (project / ".git").mkdir()
    (project / ".gitmodules").write_text("submodule\n", encoding="utf-8")
    (project / ".venv").mkdir()
    (project / ".idea").mkdir()
    monkeypatch.setattr(configure, "framework_root", _framework_override(framework))
    monkeypatch.setattr(configure, "_submodule_warning", _clean_submodule)

    configure.configure("Consumer", "Example intent.", "3.12", "generic")

    output = capsys.readouterr().out
    assert "WARNING: Preserving ignored pre-existing paths:" in output
    assert ".idea" in output
    assert ".venv" in output
    assert (project / ".idea").is_dir()
    assert (project / ".venv").is_dir()


@covers("AF-BOOT-009")
def test_submodule_registration_is_required():
    with pytest.raises(RuntimeError, match="recorded by the parent"):
        configure.validate_submodule_status(
            "-abc agent-framework\n", command_failed=False, dirty=False
        )


@covers("AF-BOOT-009")
def test_dirty_submodule_returns_warning():
    warning = configure.validate_submodule_status(
        " abc agent-framework\n", command_failed=False, dirty=True
    )

    assert warning is not None
    assert "local modifications" in warning


@covers("AF-BOOT-001", "AF-BOOT-003", "AF-BOOT-008", "AF-BOOT-011")
def test_bootstrap_skill_uses_docker_first_host_independent_path():
    skill = (ROOT / "skills" / "bootstrap-project" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "--build-arg PYTHON_VERSION=" in skill
    assert "python agent-framework/configure.py" in skill
    assert "--profile generic" in skill
    assert "init_repo" not in skill
    assert "bootstrap process feedback" in skill


@covers("AF-BOOT-002", "AF-BOOT-004", "AF-BOOT-005")
def test_bootstrap_skill_preserves_product_decision_boundary():
    skill = (ROOT / "skills" / "bootstrap-project" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "Do not strengthen the intent into" in skill
    assert "Do not create product contracts" in skill
    assert "Do not create an implementation milestone" in skill
    assert "implement product features during bootstrap" in skill


@covers("AF-DOC-001")
def test_documentation_templates_use_markdown_navigation():
    docs_readme = (ROOT / "templates" / "docs" / "README.md").read_text(
        encoding="utf-8"
    )
    contract_readme = (
        ROOT / "templates" / "docs" / "contracts" / "README.md"
    ).read_text(encoding="utf-8")
    planning_readme = (
        ROOT / "templates" / "docs" / "planning" / "README.md"
    ).read_text(encoding="utf-8")

    assert "[Contracts](contracts/README.md)" in docs_readme
    assert "[Evaluation activities](evaluation/README.md)" in contract_readme
    assert "[Roadmap](roadmap.md)" in planning_readme
    assert not (ROOT / "templates" / "docs" / "conf.py").exists()
    assert not (ROOT / "templates" / "docs" / "index.md").exists()
    for text in (docs_readme, contract_readme, planning_readme):
        assert "toctree" not in text
        assert "Sphinx" not in text


@covers("AF-DOC-002")
def test_docs_verification_uses_markdownlint_and_offline_linkcheck():
    verification = (ROOT / "agent-framework.toml").read_text(encoding="utf-8")
    linkcheck = (
        ROOT / "tools" / "documentation" / "linkcheck" / "run_linkcheck.py"
    ).read_text(encoding="utf-8")

    assert '"documentation/markdownlint"' in verification
    assert '"documentation/linkcheck"' in verification
    assert '"--offline"' in linkcheck
    assert '"--include-fragments=anchor-only"' in linkcheck
