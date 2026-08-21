from pathlib import Path

from tests.util.contract import covers

ROOT = Path(__file__).resolve().parents[1]


@covers("AF-REPO-001")
def test_framework_pre_commit_hook_is_repository_only():
    hook = ROOT / ".githooks" / "pre-commit"
    text = hook.read_text(encoding="utf-8")

    assert "docker build" in text
    assert "python tools/run_verification.py --fix" in text
    assert "MSYS_NO_PATHCONV=1" in text
    assert not (ROOT / "templates" / ".githooks").exists()
    assert "git config core.hooksPath .githooks" in (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
