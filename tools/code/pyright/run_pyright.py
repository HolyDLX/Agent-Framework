"""Run Pyright in strict mode using framework-owned generated configuration."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _framework import existing_paths, load_config, project_root
from _tool_runner import run_custom_tool, skip


def _local(arguments: list[str]) -> int:
    root = project_root()
    cfg = load_config(root)
    command = shutil.which("pyright")
    if command is None:
        return 1
    if arguments:
        return subprocess.run([command, *arguments], cwd=root, check=False).returncode
    include = existing_paths(root, cfg.source_paths + cfg.test_paths)
    if not include:
        return skip("no configured source or test paths found")
    data = {
        "include": include,
        "exclude": list(cfg.exclude_paths),
        "extraPaths": [
            *cfg.source_paths,
            "tools",
            *sorted(
                str(path.parent.relative_to(root))
                for path in (root / "tools").glob("*/*/tool.toml")
            ),
        ],
        "pythonVersion": cfg.python_version,
        "typeCheckingMode": "strict",
    }
    tmp = root / ".agent-framework-pyright.json"
    try:
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return subprocess.run(
            [command, "--project", str(tmp)], cwd=root, check=False
        ).returncode
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    return run_custom_tool(Path(__file__), _local)


if __name__ == "__main__":
    raise SystemExit(main())
