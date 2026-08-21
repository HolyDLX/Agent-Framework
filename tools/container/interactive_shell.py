"""Open an interactive shell in the project development container."""

import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from _framework import load_config, project_image_name, project_root
from container.docker_helper import (
    DEFAULT_CPUS,
    DEFAULT_MEMORY,
    WORKDIR,
    ensure_images,
)


def main() -> int:
    status = ensure_images(build_if_missing=True)
    if status:
        return status
    root = project_root()
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--interactive",
            "--tty",
            "--memory",
            DEFAULT_MEMORY,
            "--cpus",
            DEFAULT_CPUS,
            "--mount",
            f"type=bind,source={root},target={WORKDIR}",
            "--workdir",
            WORKDIR,
            project_image_name(load_config(root)),
            "bash",
        ],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
