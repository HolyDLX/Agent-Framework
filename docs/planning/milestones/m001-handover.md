# M001 handover

The flat runner inventory was replaced with eight manifest-driven categories
and thirteen discoverable tool bundles. Ordered assignments now live in
`agent-framework.toml`; aggregate fixing runs all category fix phases before all
verification phases and continues after individual failures.

The new root `toolctl.py` implementation supports inventory/status, ordered and
multi-category enablement, disablement, explicit duplicate cleanup, bundled
default display/diff/deployment/reset, unavailable-tool handling, and local
configuration warnings. Bootstrap requires an explicit profile. The initial
`generic` profile enables the accepted ten-tool baseline and seeds thin
project-owned `toolctl.py` and `run_verification.py` wrappers.

Concise latest-run logs cover category, aggregate verification, and Docker build
entry points. Aggregate logs contain complete nested output; failures print an
uninterpreted tail and log location.

Host verification completed with 36 passing tests, Black, Ruff, pydoclint,
Pyright, yamllint, markdownlint-cli2, contract traceability, and the new
aggregate fix/verify workflow.

The canonical container workflow was subsequently verified on Windows using
PowerShell:

`python.exe .\tools\run_verification.py --fix --container`

All eight categories passed during both the fix and verification phases,
including the documentation, shell, and CI categories that were unavailable
during host-only verification in the implementation environment.
