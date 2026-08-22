import argparse
import sys
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import run_verification
from _category_runner import run_category
from _latest_log import CommandResult, print_tail, write_latest
from _tool_catalog import Catalog, Category, Operation, ToolBundle, discover_catalog
from _tool_config import load_assignments

import toolctl


def _config(root: Path, content: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "agent-framework.toml").write_text(content, encoding="utf-8")


@covers("AF-TOOL-005")
def test_catalog_discovers_categories_and_bundles():
    catalog = discover_catalog(ROOT / "tools")

    assert not catalog.errors
    assert "code" in catalog.categories
    assert catalog.tools["code/black"].operations["fix"].arguments == ("--fix",)
    assert catalog.tools["contracts/traceability"].native_category == "contracts"


@covers("AF-TOOL-010")
def test_toolctl_enable_is_ordered_idempotent_and_preserves_other_config(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    _config(tmp_path, '[project]\nname = "example"\n')
    monkeypatch.setattr(toolctl, "project_root", lambda: tmp_path)

    assert toolctl.main(["enable", "ruff"]) == 0
    first = (tmp_path / "agent-framework.toml").read_text(encoding="utf-8")
    assert toolctl.main(["enable", "RUFF"]) == 0
    second = (tmp_path / "agent-framework.toml").read_text(encoding="utf-8")

    assert first == second
    assert first.startswith('[project]\nname = "example"\n')
    assert load_assignments(tmp_path) == {"code": ["code/ruff"]}


@covers("AF-TOOL-010")
def test_unknown_tool_lists_available_tools(
    tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    _config(tmp_path, '[project]\nname = "example"\n')
    monkeypatch.setattr(toolctl, "project_root", lambda: tmp_path)

    assert toolctl.main(["enable", "missing"]) == 2

    output = capsys.readouterr()
    assert "Unknown tool" in output.err
    assert "Available tools:" in output.out
    assert "code/black" in output.out


@covers("AF-TOOL-010")
def test_fix_duplicates_keeps_first_assignment(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    _config(
        tmp_path,
        "# BEGIN MANAGED TOOL CONFIGURATION\n"
        '[tools.code]\nenabled = ["code/ruff", "code/black", "code/ruff"]\n'
        "# END MANAGED TOOL CONFIGURATION\n",
    )
    monkeypatch.setattr(toolctl, "project_root", lambda: tmp_path)

    assert toolctl.main(["fix-duplicates"]) == 0

    assert load_assignments(tmp_path)["code"] == ["code/ruff", "code/black"]


@covers("AF-TOOL-011")
def test_defaults_can_be_deployed_diffed_and_force_reset(
    tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    _config(
        tmp_path,
        '[project]\nname = "example"\npython_version = "3.12"\n'
        "[verification]\nline_length = 88\n",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "example"\n', encoding="utf-8"
    )
    monkeypatch.setattr(toolctl, "project_root", lambda: tmp_path)

    assert toolctl.main(["enable", "black", "--with-defaults"]) == 0
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '[project]\nname = "example"' in pyproject
    assert "[tool.black]" in pyproject
    assert toolctl.main(["diff-defaults", "black"]) == 0
    assert "no differences" in capsys.readouterr().out

    (tmp_path / "pyproject.toml").write_text(
        pyproject.replace("line-length = 88", "line-length = 100"), encoding="utf-8"
    )
    assert toolctl.main(["reset-defaults", "black"]) == 2
    assert toolctl.main(["reset-defaults", "black", "--force"]) == 0
    reset = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "line-length = 88" in reset
    assert '[project]\nname = "example"' in reset


@covers("AF-TOOL-006", "AF-TOOL-007", "AF-TOOL-013")
def test_category_runs_first_duplicate_in_configuration_order(
    tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    _config(
        tmp_path,
        '[tools.code]\nenabled = ["code/second", "code/first", "code/second"]\n',
    )
    scripts = {}
    bundles: dict[str, ToolBundle] = {}
    for name in ("first", "second"):
        script = tmp_path / f"{name}.py"
        script.write_text("", encoding="utf-8")
        scripts[name] = script
        bundles[f"code/{name}"] = ToolBundle(
            identifier=f"code/{name}",
            short_name=name,
            native_category="code",
            display_name=name,
            directory=tmp_path,
            operations={"verify": Operation(script, ())},
            configuration=(),
        )
    category_script = tmp_path / "category.py"
    category_script.write_text("", encoding="utf-8")
    catalog = Catalog(
        categories={
            "code": Category("code", tmp_path, category_script, category_script)
        },
        tools=bundles,
        errors=(),
    )
    calls: list[str] = []

    def fake_capture(command: list[str], **_kwargs: object) -> CommandResult:
        calls.append(Path(command[1]).stem)
        return CommandResult(0, "", 0.1)

    monkeypatch.setattr("_category_runner.project_root", lambda: tmp_path)
    monkeypatch.setattr("_category_runner.discover_catalog", lambda: catalog)
    monkeypatch.setattr("_category_runner.capture", fake_capture)
    args = argparse.Namespace(
        verbose=False, ignore_unavailable=False, _emit_full_output=False
    )

    assert run_category("code", "verify", args) == 0
    assert calls == ["second", "first"]
    assert "appears multiple times" in capsys.readouterr().out

    calls.clear()
    assert run_category("code", "fix", args) == 0
    assert not calls
    assert "no fix operation" in capsys.readouterr().out


@covers("AF-TOOL-012")
def test_latest_log_is_replaced_and_failure_tail_is_uninterpreted(
    tmp_path: Path, capsys: CaptureFixture[str]
):
    path = tmp_path / ".agent-framework" / "logs" / "example" / "latest.log"

    write_latest(path, "old\n")
    write_latest(path, "first\nsecond\nthird\n")
    print_tail(path.read_text(encoding="utf-8"), lines=2)

    assert path.read_text(encoding="utf-8") == "first\nsecond\nthird\n"
    assert capsys.readouterr().out == "second\nthird\n"


@covers("AF-TOOL-008")
def test_aggregate_runs_all_fixes_before_all_verifications(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    _config(
        tmp_path,
        '[tools.documentation]\nenabled = ["documentation/linkcheck"]\n'
        '[tools.code]\nenabled = ["code/black"]\n',
    )
    calls: list[str] = []

    def fake_capture(command: list[str], **_kwargs: object) -> CommandResult:
        calls.append(Path(command[1]).name)
        return CommandResult(1 if len(calls) == 1 else 0, "failure\n", 0.1)

    monkeypatch.setattr(run_verification, "project_root", lambda: tmp_path)
    monkeypatch.setattr(run_verification, "capture", fake_capture)

    assert run_verification.run_configured(["--fix"]) == 1
    assert calls == [
        "fix_documentation.py",
        "fix_code.py",
        "verify_documentation.py",
        "verify_code.py",
    ]


@covers("AF-TOOL-009")
def test_unavailable_tool_fails_unless_explicitly_ignored(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    _config(
        tmp_path,
        '[tools.code]\nenabled = ["code/removed"]\n',
    )
    calls: list[list[str]] = []

    def fake_capture(command: list[str], **_kwargs: object) -> CommandResult:
        calls.append(command)
        return CommandResult(0, "", 0.1)

    monkeypatch.setattr(run_verification, "project_root", lambda: tmp_path)
    monkeypatch.setattr(run_verification, "capture", fake_capture)

    assert run_verification.run_configured([]) == 2
    assert not calls
    assert run_verification.run_configured(["--ignore-unavailable"]) == 0
    assert calls
    assert "--ignore-unavailable" in calls[0]
