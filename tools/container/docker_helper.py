"""Build/check framework base and project development Docker images."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from _framework import (
    FRAMEWORK_ROOT,
    framework_tool_path,
    load_config,
    project_image_name,
    project_root,
)

WORKDIR = "/workspace"
DEFAULT_MEMORY = "512m"
DEFAULT_CPUS = "2"


def _docker_available() -> bool:
    docker = shutil.which("docker")
    if docker is None:
        print("Docker was not found on PATH.", file=sys.stderr)
        return False
    result = subprocess.run(
        [docker, "info"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("Docker is installed but its service is unavailable.", file=sys.stderr)
        details = (result.stderr or result.stdout).strip()
        if details:
            print(details, file=sys.stderr)
        return False
    return True


def _image_exists(image: str) -> bool:
    return (
        subprocess.run(
            ["docker", "image", "inspect", image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _base_image_name(python_version: str) -> str:
    """Return the version-specific framework base-image name."""

    return f"agent-framework-python:{python_version}-local"


def _build_base(image: str, python_version: str) -> int:
    return subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"PYTHON_VERSION={python_version}",
            "--tag",
            image,
            "--file",
            str(FRAMEWORK_ROOT / "container" / "Dockerfile"),
            str(FRAMEWORK_ROOT / "container"),
        ],
        check=False,
    ).returncode


def _build_project(image: str, base_image: str) -> int:
    root = project_root()
    dockerfile = root / "Dockerfile"
    if not dockerfile.exists():
        print(f"Missing project Dockerfile: {dockerfile}", file=sys.stderr)
        return 1
    return subprocess.run(
        [
            "docker",
            "build",
            "--tag",
            image,
            "--build-arg",
            f"AGENT_FRAMEWORK_BASE_IMAGE={base_image}",
            "--file",
            str(dockerfile),
            str(root),
        ],
        check=False,
    ).returncode


def ensure_images(*, rebuild: bool = False, build_if_missing: bool = False) -> int:
    if not _docker_available():
        return 125
    config = load_config()
    base_image = _base_image_name(config.python_version)
    project_image = project_image_name(config)

    if rebuild or not _image_exists(base_image):
        result = _build_base(base_image, config.python_version)
        if result:
            return result
    elif build_if_missing:
        pass

    if rebuild or not _image_exists(project_image):
        result = _build_project(project_image, base_image)
        if result:
            return result
    return 0


def run_in_container(script: Path, arguments: Sequence[str]) -> int:
    """Run one framework runner inside the project development image."""
    status = ensure_images(build_if_missing=True)
    if status:
        return status
    root = project_root()
    image = project_image_name(load_config(root))
    command = [
        "docker",
        "run",
        "--rm",
        "--memory",
        DEFAULT_MEMORY,
        "--cpus",
        DEFAULT_CPUS,
        "--mount",
        f"type=bind,source={root},target={WORKDIR}",
        "--workdir",
        WORKDIR,
        image,
        "python",
        framework_tool_path(script),
        *arguments,
    ]
    if os.name != "nt" and hasattr(os, "getuid") and hasattr(os, "getgid"):
        command[3:3] = [
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--env",
            "HOME=/tmp",
        ]
    return subprocess.run(command, cwd=root, check=False).returncode


def _parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rebuild", action="store_true")
    group.add_argument("--build-if-missing", action="store_true")
    parser.add_argument("--print-image", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse()
    if args.print_image:
        print(project_image_name(load_config()))
        return 0
    if not (args.rebuild or args.build_if_missing):
        if not _docker_available():
            return 125
        base = _image_exists(_base_image_name(load_config().python_version))
        project = _image_exists(project_image_name(load_config()))
        print(f"base={base} project={project}")
        return 0 if base and project else 1
    return ensure_images(rebuild=args.rebuild, build_if_missing=args.build_if_missing)


if __name__ == "__main__":
    raise SystemExit(main())
