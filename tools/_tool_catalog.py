"""Discover Agent Framework category and tool bundle manifests."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import tomllib

TOOLS_ROOT = Path(__file__).resolve().parent
IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9_-]*")


class CatalogError(ValueError):
    """Raised when a category or tool manifest is invalid."""


@dataclass(frozen=True)
class Operation:
    script: Path
    arguments: tuple[str, ...]


@dataclass(frozen=True)
class ConfigurationArtifact:
    default: Path
    target: Path
    section: str | None = None


@dataclass(frozen=True)
class ToolBundle:
    identifier: str
    short_name: str
    native_category: str
    display_name: str
    directory: Path
    operations: dict[str, Operation]
    configuration: tuple[ConfigurationArtifact, ...]


@dataclass(frozen=True)
class Category:
    identifier: str
    directory: Path
    verify: Path
    fix: Path


@dataclass(frozen=True)
class Catalog:
    categories: dict[str, Category]
    tools: dict[str, ToolBundle]
    errors: tuple[str, ...]

    def resolve(self, value: str) -> ToolBundle:
        """Resolve a canonical or globally unique short tool name."""

        normalized = normalize_tool_reference(value)
        if "/" in normalized:
            tool = self.tools.get(normalized)
            if tool is None:
                raise CatalogError(f"Unknown tool: {normalized}")
            return tool
        matches = [
            tool for tool in self.tools.values() if tool.short_name == normalized
        ]
        if not matches:
            raise CatalogError(f"Unknown tool: {normalized}")
        if len(matches) > 1:
            choices = "\n  ".join(sorted(tool.identifier for tool in matches))
            raise CatalogError(
                f"Tool name {normalized!r} is ambiguous. Specify one of:\n  {choices}"
            )
        return matches[0]


def normalize_identifier(value: str) -> str:
    """Return a validated lowercase category or tool identifier."""

    normalized = value.strip().lower()
    if IDENTIFIER.fullmatch(normalized) is None:
        raise CatalogError(
            f"Invalid identifier {value!r}; use letters, digits, '_' or '-', "
            "starting with a letter or digit."
        )
    return normalized


def normalize_tool_reference(value: str) -> str:
    """Normalize a short or category-qualified tool reference."""

    parts = value.strip().lower().replace("\\", "/").split("/")
    if len(parts) not in (1, 2):
        raise CatalogError(f"Invalid tool reference: {value!r}")
    return "/".join(normalize_identifier(part) for part in parts)


def _table(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise CatalogError(f"{context} must be a TOML table")
    return cast(dict[str, object], value)


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{context} must be a non-empty string")
    return value


def _safe_relative(directory: Path, value: object, context: str) -> Path:
    relative = Path(_string(value, context))
    if relative.is_absolute() or ".." in relative.parts:
        raise CatalogError(f"{context} must stay inside its bundle")
    resolved = (directory / relative).resolve()
    if directory.resolve() not in resolved.parents or not resolved.is_file():
        raise CatalogError(f"{context} does not identify a bundle file: {relative}")
    return resolved


def _load_category(path: Path) -> Category:
    raw = _table(tomllib.loads(path.read_text(encoding="utf-8")), str(path))
    identifier = normalize_identifier(_string(raw.get("id"), f"{path}: id"))
    if identifier != path.parent.name:
        raise CatalogError(f"{path}: id must match directory name")
    return Category(
        identifier=identifier,
        directory=path.parent,
        verify=_safe_relative(path.parent, raw.get("verify"), f"{path}: verify"),
        fix=_safe_relative(path.parent, raw.get("fix"), f"{path}: fix"),
    )


def _string_list(value: object, context: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in cast(list[object], value)
    ):
        raise CatalogError(f"{context} must be an array of strings")
    return tuple(cast(str, item) for item in cast(list[object], value))


def _load_tool(path: Path, category: Category) -> ToolBundle:
    raw = _table(tomllib.loads(path.read_text(encoding="utf-8")), str(path))
    short_name = normalize_identifier(_string(raw.get("id"), f"{path}: id"))
    if short_name != path.parent.name:
        raise CatalogError(f"{path}: id must match directory name")
    display = raw.get("name", short_name)
    display_name = _string(display, f"{path}: name")
    operations_raw = _table(raw.get("operations"), f"{path}: operations")
    operations: dict[str, Operation] = {}
    for operation_name, operation_value in operations_raw.items():
        if operation_name not in {"verify", "fix"}:
            raise CatalogError(f"{path}: unsupported operation {operation_name!r}")
        operation = _table(operation_value, f"{path}: operations.{operation_name}")
        operations[operation_name] = Operation(
            script=_safe_relative(
                path.parent,
                operation.get("script"),
                f"{path}: operations.{operation_name}.script",
            ),
            arguments=_string_list(
                operation.get("arguments"),
                f"{path}: operations.{operation_name}.arguments",
            ),
        )
    if "verify" not in operations:
        raise CatalogError(f"{path}: a verify operation is required")

    configuration: list[ConfigurationArtifact] = []
    raw_configuration = raw.get("configuration", [])
    if not isinstance(raw_configuration, list):
        raise CatalogError(f"{path}: configuration must be an array of tables")
    for index, item in enumerate(cast(list[object], raw_configuration)):
        artifact = _table(item, f"{path}: configuration[{index}]")
        target = Path(_string(artifact.get("target"), f"{path}: target"))
        if target.is_absolute() or ".." in target.parts:
            raise CatalogError(f"{path}: configuration target must be project-relative")
        section_value = artifact.get("section")
        if section_value is not None and not isinstance(section_value, str):
            raise CatalogError(f"{path}: configuration section must be a string")
        configuration.append(
            ConfigurationArtifact(
                default=_safe_relative(
                    path.parent, artifact.get("default"), f"{path}: default"
                ),
                target=target,
                section=section_value,
            )
        )
    return ToolBundle(
        identifier=f"{category.identifier}/{short_name}",
        short_name=short_name,
        native_category=category.identifier,
        display_name=display_name,
        directory=path.parent,
        operations=operations,
        configuration=tuple(configuration),
    )


def discover_catalog(tools_root: Path = TOOLS_ROOT) -> Catalog:
    """Discover valid manifests and retain diagnostics for invalid bundles."""

    categories: dict[str, Category] = {}
    tools: dict[str, ToolBundle] = {}
    errors: list[str] = []
    for path in sorted(tools_root.glob("*/category.toml")):
        try:
            category = _load_category(path)
        except (CatalogError, OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(str(exc))
            continue
        categories[category.identifier] = category
        for manifest in sorted(category.directory.glob("*/tool.toml")):
            try:
                tool = _load_tool(manifest, category)
            except (CatalogError, OSError, tomllib.TOMLDecodeError) as exc:
                errors.append(str(exc))
                continue
            if tool.identifier in tools:
                errors.append(f"Duplicate tool identifier: {tool.identifier}")
                continue
            tools[tool.identifier] = tool
    return Catalog(categories=categories, tools=tools, errors=tuple(errors))
