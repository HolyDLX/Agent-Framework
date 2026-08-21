"""Local-execution policy for framework verification runners."""

from __future__ import annotations

import os

ALLOW_ENV = "AGENT_FRAMEWORK_ALLOW_LOCAL"
CONTAINER_ENV = "RUNNING_IN_CONTAINER"


def is_running_in_container() -> bool:
    return os.environ.get(CONTAINER_ENV) == "1"


def is_local_execution_allowed() -> bool:
    return os.environ.get(ALLOW_ENV) == "1"


def assert_local_execution_allowed() -> None:
    if is_local_execution_allowed() or is_running_in_container():
        return
    raise SystemExit(
        "Local execution is disabled for framework runners. Use --container. "
        "A human who intentionally wants host execution may run "
        "tools/container/allow_local.py (framework standalone) or "
        "agent-framework/tools/container/allow_local.py (consumer project)."
    )
