import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from _documentation import markdown_files


def test_markdown_files_excludes_framework_submodule_for_consumer(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
    framework = tmp_path / "agent-framework"
    framework.mkdir()
    (framework / "README.md").write_text("# Framework\n", encoding="utf-8")
    cache = tmp_path / ".pytest_cache"
    cache.mkdir()
    (cache / "ignored.md").write_text("# Ignore\n", encoding="utf-8")

    assert markdown_files(tmp_path) == ["README.md", "docs/guide.md"]


def test_markdown_files_are_stably_sorted(tmp_path: Path):
    (tmp_path / "z.md").write_text("# Z\n", encoding="utf-8")
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")

    assert markdown_files(tmp_path) == ["a.md", "z.md"]
