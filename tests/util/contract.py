"""Test-only contract traceability decorator."""

from __future__ import annotations

from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def covers(*requirement_ids: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Attach literal requirement IDs for static traceability extraction."""
    if not requirement_ids or any(not item for item in requirement_ids):
        raise ValueError("covers() requires one or more non-empty requirement IDs")

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        setattr(  # noqa: B010 - intentional test metadata
            function, "__contract_requirements__", tuple(requirement_ids)
        )
        return function

    return decorator
