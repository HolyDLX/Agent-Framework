# Framework contract

## Project/framework ownership boundary

**AF-OWN-001** — Standard verification runners supplied by Agent Framework shall
remain framework-owned and shall operate on the consuming project without
requiring copied project-local runner forks.
Type: `structural`

**AF-OWN-002** — Project configuration shall complete its preflight before
writing files and shall fail without modifying the consuming project when an
existing path conflicts with the intended scaffold.
Type: `behavioral`

**AF-OWN-003** — A normal consuming-project agent shall use the consuming
project's root `AGENTS.md` as its onboarding entry point rather than the
framework submodule's `AGENTS.md`.
Type: `process`

## Container boundary

**AF-CONT-001** — The framework base image shall contain the dependencies
required to execute every standard framework verification runner.
Type: `structural`

**AF-CONT-002** — A consuming project's development image shall be built on top
of the framework base image and may add project/package dependencies without
reinstalling the framework toolchain.
Type: `structural`

## Bootstrap boundary

**AF-BOOT-001** — Project bootstrap shall be executable on a Windows host with
Git and Docker without requiring host Bash, WSL, host Python, or host Linux
verification tools.
Type: `process`

**AF-BOOT-002** — Bootstrap shall preserve unresolved product decisions when
those decisions are not required to establish project identity, repository
shape, or another bootstrap prerequisite.
Type: `process`

**AF-BOOT-003** — The bootstrap agent shall finish with explicit process
feedback for the framework author, including encountered friction or an
explicit statement that no workflow issues were found.
Type: `process`

**AF-BOOT-004** — Bootstrap shall not strengthen a developer-supplied product
goal into additional externally observable guarantees that have not already
been settled.
Type: `process`

**AF-BOOT-005** — Bootstrap shall seed the planning, contract, and evaluation
document structure without creating product contracts, evaluation activities,
roadmap commitments, or implementation milestones.
Type: `process`

**AF-BOOT-006** — Project configuration shall require a project name and initial
intent and shall deterministically create the project metadata, `src/` package,
minimal executable scaffold, import-and-call smoke test, root README, and
architecture intent baseline from those inputs.
Type: `behavioral`

**AF-BOOT-007** — Project configuration shall reject a project name that cannot
be normalized into a valid non-keyword Python import-package identifier using
the documented ASCII naming rules.
Type: `behavioral`

**AF-BOOT-008** — Project configuration shall support Python 3.12 and 3.14,
default to Python 3.12, and use the selected version consistently in project
metadata and the framework base image build.
Type: `behavioral`

**AF-BOOT-009** — Project configuration shall require `agent-framework/` to be
an initialized Git submodule checked out at the parent repository's recorded
commit while reporting local submodule modifications as a warning rather than
a failure.
Type: `behavioral`

**AF-BOOT-010** — Project configuration shall reject unexpected consuming-root
entries, allow and warn about entries matched by the seeded `.gitignore`, and
otherwise permit only `.git`, `.gitmodules`, and `agent-framework` before
configuration.
Type: `behavioral`

## Verification-tool behavior

**AF-TOOL-001** — The framework Black runner shall target the Python version
configured by `project.python_version` rather than relying on Black's inferred
future-version target.
Type: `behavioral`

**AF-TOOL-002** — The framework Ruff runner shall not report `EXE002` solely
because Windows bind-mount semantics make Python files appear executable inside
the Linux development container.
Type: `behavioral`

**AF-TOOL-003** — The AI sanitizer shall report possible direct milestone
references found outside project planning documentation as advisory review
findings without making those findings a verification failure.
Type: `behavioral`

**AF-TOOL-004** — The traceability generator shall accept an explicitly planned
`automated-test` evaluation activity without current `@covers(...)` evidence and
shall report that requirement as `PLANNED-AUTOMATED` rather than missing
automated evidence.
Type: `behavioral`

## Documentation scaffold

**AF-DOC-001** — Framework-seeded project documentation shall use ordinary
repository-relative Markdown links for navigation rather than requiring Sphinx
or MyST navigation metadata.
Type: `structural`

**AF-DOC-002** — The framework documentation verification group shall lint
project-owned Markdown and validate repository-local Markdown links without
requiring network access.
Type: `behavioral`

**AF-SCAFF-001** — Framework-seeded `tests/util/contract.py` shall be compatible
with the framework's Ruff and Pyright verification policies without requiring a
consuming-project-specific suppression or rewrite.
Type: `structural`

## Framework repository verification

**AF-REPO-001** — The Agent Framework repository shall provide a repository-only
pre-commit gate that runs complete framework verification in the controlled
Docker environment and shall not seed that hook into consuming projects.
Type: `process`
