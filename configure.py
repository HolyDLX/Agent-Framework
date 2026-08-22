"""Configure a clean consuming repository from Agent Framework templates."""

from __future__ import annotations

import argparse
import fnmatch
import json
import keyword
import re
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template
from typing import cast

import tomllib

SUPPORTED_PYTHON_VERSIONS = ("3.12", "3.14")
ALLOWED_ROOT_ENTRIES = frozenset({".git", ".gitmodules", "agent-framework"})
RENDERED_DESTINATIONS = {
    "Dockerfile": "Dockerfile",
    "README.md": "README.md",
    "agent-framework.toml": "agent-framework.toml",
    "pyproject.toml": "pyproject.toml",
    "rendered/package/__init__.py.template": "src/{package_name}/__init__.py",
    "rendered/package/main.py.template": "src/{package_name}/main.py",
    "rendered/tests/test_main.py.template": "tests/test_main.py",
    "rendered/toolctl.py.template": "toolctl.py",
    "rendered/run_verification.py.template": "run_verification.py",
    "docs/architecture/README.md": "docs/architecture/README.md",
    "docs/development/container.md": "docs/development/container.md",
}


def parse_arguments() -> argparse.Namespace:
    """Parse project configuration inputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-name", required=True, help="project display name")
    parser.add_argument("--intent", required=True, help="initial project intent")
    parser.add_argument("--profile", help="required bootstrap profile name")
    parser.add_argument(
        "--python-version",
        choices=SUPPORTED_PYTHON_VERSIONS,
        default="3.12",
        help="supported Python minor version (default: 3.12)",
    )
    arguments = parser.parse_args()
    if arguments.profile is None:
        available = sorted(
            path.parent.name
            for path in Path(__file__).resolve().parent.glob("profiles/*/profile.toml")
        )
        parser.error(
            "a bootstrap profile is required; available profiles: "
            + (", ".join(available) or "none")
        )
    return arguments


def load_profile(root: Path, name: str) -> tuple[Path, str]:
    """Return the validated profile template root and rendered tool section."""

    normalized = name.strip().lower()
    if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", normalized) is None:
        raise ValueError(f"Invalid bootstrap profile: {name!r}")
    profile_path = root / "profiles" / normalized / "profile.toml"
    if not profile_path.is_file():
        available = sorted(
            path.parent.name for path in root.glob("profiles/*/profile.toml")
        )
        choices = ", ".join(available) or "none"
        raise ValueError(
            f"Unknown bootstrap profile {normalized!r}. Available: {choices}"
        )
    raw = tomllib.loads(profile_path.read_text(encoding="utf-8"))
    template_value = raw.get("template_root")
    if not isinstance(template_value, str):
        raise TypeError(f"Profile {normalized!r} has no template_root")
    template_root = (profile_path.parent / template_value).resolve()
    if root.resolve() not in template_root.parents or not template_root.is_dir():
        raise ValueError(f"Profile {normalized!r} has an invalid template_root")
    raw_tools = raw.get("tools")
    if not isinstance(raw_tools, dict):
        raise TypeError(f"Profile {normalized!r} has no [tools] assignments")
    lines = ["# BEGIN MANAGED TOOL CONFIGURATION"]
    for category, value in cast(dict[object, object], raw_tools).items():
        if not isinstance(category, str) or not isinstance(value, dict):
            raise TypeError(f"Profile {normalized!r} has invalid tool assignments")
        enabled = cast(dict[object, object], value).get("enabled")
        if not isinstance(enabled, list) or not all(
            isinstance(item, str) for item in cast(list[object], enabled)
        ):
            raise TypeError(
                f"Profile {normalized!r} has invalid tools.{category}.enabled"
            )
        lines.extend((f"[tools.{category}]", "enabled = ["))
        for item in cast(list[object], enabled):
            identifier = cast(str, item)
            parts = identifier.split("/")
            if (
                len(parts) != 2
                or not (root / "tools" / parts[0] / parts[1] / "tool.toml").is_file()
            ):
                raise ValueError(
                    f"Profile {normalized!r} references unavailable tool "
                    f"{identifier!r}"
                )
            lines.append(f'    "{identifier}",')
        lines.extend(("]", ""))
    if lines[-1] == "":
        lines.pop()
    lines.append("# END MANAGED TOOL CONFIGURATION")
    return template_root, "\n".join(lines)


def framework_root() -> Path:
    """Return and validate the framework checkout root."""

    root = Path(__file__).resolve().parent
    if root.name != "agent-framework":
        raise RuntimeError("Expected framework checkout at <project>/agent-framework.")
    return root


def normalized_names(project_name: str) -> tuple[str, str, str]:
    """Return validated display, distribution, and import-package names."""

    display_name = project_name.strip()
    if not display_name:
        raise ValueError("--project-name must not be empty.")
    if re.fullmatch(r"[A-Za-z0-9 _-]+", display_name) is None:
        raise ValueError(
            "--project-name may contain only ASCII letters, digits, spaces, "
            "underscores, and hyphens."
        )

    distribution_name = re.sub(r"[ _-]+", "-", display_name.lower()).strip("-")
    package_name = distribution_name.replace("-", "_")
    if not package_name.isidentifier() or keyword.iskeyword(package_name):
        raise ValueError(
            f"Derived import package {package_name!r} is not a valid, non-keyword "
            "Python identifier; choose another --project-name."
        )
    return display_name, distribution_name, package_name


def _ignore_patterns(path: Path) -> tuple[str, ...]:
    """Return active root-level patterns from the template gitignore."""

    patterns: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith(("#", "!")):
            patterns.append(line.rstrip("/"))
    return tuple(patterns)


def _matches_root_ignore(name: str, patterns: tuple[str, ...]) -> bool:
    """Return whether a root entry matches a template ignore pattern."""

    return any(
        "/" not in pattern and fnmatch.fnmatchcase(name, pattern)
        for pattern in patterns
    )


def validate_submodule_status(
    output: str, *, command_failed: bool, dirty: bool
) -> str | None:
    """Validate captured submodule state and return a dirty-tree warning."""

    output = output.rstrip("\n")
    if command_failed or not output:
        raise RuntimeError(
            "agent-framework/ must be registered and initialized as a Git submodule."
        )
    if "\n" in output or output[0] != " ":
        raise RuntimeError(
            "agent-framework/ must be initialized at the commit recorded by the "
            f"parent repository; git submodule status returned: {output!r}"
        )

    if dirty:
        return "agent-framework/ contains local modifications or untracked files"
    return None


def _submodule_warning(project_root: Path, root: Path) -> str | None:
    """Inspect submodule registration and local working-tree state."""

    status = subprocess.run(
        ["git", "submodule", "status", "--", "agent-framework"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if dirty.returncode:
        raise RuntimeError("Could not inspect the agent-framework submodule status.")
    return validate_submodule_status(
        status.stdout,
        command_failed=bool(status.returncode),
        dirty=bool(dirty.stdout.strip()),
    )


def preflight(root: Path) -> tuple[list[str], str | None]:
    """Validate the clean-project boundary before any file is written."""

    project_root = root.parent
    patterns = _ignore_patterns(root / "templates" / ".gitignore")
    unexpected: list[str] = []
    ignored: list[str] = []

    for entry in sorted(project_root.iterdir(), key=lambda path: path.name):
        if entry.name in ALLOWED_ROOT_ENTRIES:
            continue
        if _matches_root_ignore(entry.name, patterns):
            ignored.append(entry.name)
        else:
            unexpected.append(entry.name)

    if unexpected:
        formatted = "\n  ".join(unexpected)
        raise RuntimeError(
            "Configuration supports only a clean consuming repository. "
            "Unexpected root paths were found:\n"
            f"  {formatted}\n"
            "No files were changed. Move or remove these paths manually before "
            "running configuration."
        )

    return ignored, _submodule_warning(project_root, root)


def _static_templates(template_root: Path) -> list[Path]:
    """Return static seed files in stable relative-path order."""

    rendered_root = template_root / "rendered"
    rendered_sources = {
        (template_root / source).resolve() for source in RENDERED_DESTINATIONS
    }
    return sorted(
        path
        for path in template_root.rglob("*")
        if path.is_file()
        and path.resolve() not in rendered_sources
        and rendered_root not in path.parents
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )


def _rendered_files(
    template_root: Path,
    values: dict[str, str],
) -> list[tuple[Path, str]]:
    """Return rendered destination paths and text."""

    result: list[tuple[Path, str]] = []
    for source_name, destination_pattern in RENDERED_DESTINATIONS.items():
        source = template_root / source_name
        if not source.is_file():
            raise RuntimeError(f"Missing rendered template: {source_name}")
        destination = Path(destination_pattern.format(**values))
        content = Template(source.read_text(encoding="utf-8")).substitute(values)
        result.append((destination, content))
    return result


def configure(
    project_name: str, intent: str, python_version: str, profile: str
) -> None:
    """Create the complete initial scaffold after successful preflight."""

    root = framework_root()
    project_root = root.parent
    template_root, tool_configuration = load_profile(root, profile)
    display_name, distribution_name, package_name = normalized_names(project_name)
    if not intent.strip():
        raise ValueError("--intent must not be empty.")

    ignored, submodule_warning = preflight(root)
    values = {
        "display_name": display_name,
        "distribution_name": distribution_name,
        "package_name": package_name,
        "python_version": python_version,
        "intent": intent,
        "intent_toml": json.dumps(intent, ensure_ascii=False),
        "image_name": f"agent-{distribution_name}-development",
        "tool_configuration": tool_configuration,
    }
    static = [
        (source.relative_to(template_root), source)
        for source in _static_templates(template_root)
    ]
    rendered = _rendered_files(template_root, values)
    destinations = [relative for relative, _ in static] + [
        relative for relative, _ in rendered
    ]
    conflicts = sorted(
        relative.as_posix()
        for relative in destinations
        if (project_root / relative).exists()
    )
    if conflicts:
        formatted = "\n  ".join(conflicts)
        raise RuntimeError(
            "Configuration would overwrite existing paths:\n"
            f"  {formatted}\nNo files were changed."
        )

    if ignored:
        print("WARNING: Preserving ignored pre-existing paths:")
        for path in ignored:
            print(f"  {path}")
        print(
            "These paths are tolerated pre-existing state, not required bootstrap state."
        )
    if submodule_warning:
        print(f"WARNING: {submodule_warning}.")

    created_files: list[Path] = []
    try:
        for relative, source in static:
            destination = project_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            created_files.append(destination)
            print(f"CREATE  {relative.as_posix()}")
        for relative, content in rendered:
            destination = project_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
            created_files.append(destination)
            print(f"CREATE  {relative.as_posix()}")
    except OSError:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        raise

    print()
    print("Project configuration complete.")
    print(f"Display name:      {display_name}")
    print(f"Distribution name: {distribution_name}")
    print(f"Import package:    {package_name}")
    print(f"Python version:    {python_version}")
    print(f"Bootstrap profile: {profile.strip().lower()}")
    print(f"Development image: agent-{distribution_name}-development")
    print(f"Generated files:   {len(created_files)}")


def main() -> int:
    """Run project configuration."""

    args = parse_arguments()
    try:
        configure(args.project_name, args.intent, args.python_version, args.profile)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
