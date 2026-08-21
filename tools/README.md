# Framework tools

These runners are framework-owned and operate on either the consuming project
(parent of the visible `agent-framework/` submodule) or this repository when
run standalone.

Complete verification is performed by `run_verification.py` inside the project
development container. A Docker-only host can launch it directly:

```text
docker run --rm --mount type=bind,source=<project-root>,target=/workspace --workdir /workspace <project-development-image> python agent-framework/tools/run_verification.py
```

When host Python is intentionally available, this convenience dispatcher builds
images as needed and launches the same runner:

```text
python agent-framework/tools/run_verification.py --container
```

Standard runners:

- `run_black.py`
- `run_ruff.py`
- `run_pydoclint.py`
- `run_pyright.py`
- `run_pytest.py`
- `run_coverage.py`
- `run_markdownlint.py`
- `run_linkcheck.py`
- `run_ai_sanitizer.py`
- `run_contracts.py`
- `run_shellcheck.py`
- `run_yamllint.py`
- `run_actionlint.py`
- `run_verification.py`

`run_ai_sanitizer.py` includes an advisory review for possible direct milestone
references outside `docs/planning/`. Because the check is heuristic, it reports
file/line locations for agent review without changing the sanitizer exit status.

Project variation is expressed through supported `agent-framework.toml` fields,
not by copying and modifying these runners.

## Documentation verification

`run_markdownlint.py` applies the framework-owned Markdown style policy to
project-owned Markdown files. It supports `--fix` for deterministic lint fixes.

`run_linkcheck.py` uses lychee in offline mode to validate repository-local
Markdown links and anchors. External HTTP/HTTPS availability is deliberately not
part of the local verification gate. In consuming projects, the framework
submodule is excluded so each repository verifies the Markdown it owns.

## Coverage exclusions

`verification.coverage_exclude_paths` in `agent-framework.toml` lists files or
patterns that coverage.py omits from measurement and from terminal, HTML, and
XML reports. Use this only for code whose correctness is established through a
different verification mechanism, such as thin framework runner adapters that
are executed by the verification pipeline itself. Do not use it to hide
untested application or framework logic.
