# Framework evaluation activities

## EA-AF-OWN-001

Requirements: `AF-OWN-001`
Method: `inspection`

Inspect the framework runner inventory and consumer templates. Verify standard
runners live under `tools/`, while consumer templates invoke them through the
`agent-framework/` path and do not copy runner implementations.

## EA-AF-OWN-002

Requirements: `AF-OWN-002`
Method: `automated-test`

Create a temporary consuming-project fixture containing a conflicting scaffold
path, invoke `configure.py`, and verify configuration fails before creating any
other project file.

## EA-AF-OWN-003

Requirements: `AF-OWN-003`
Method: `inspection`

Inspect `templates/AGENTS.md` and verify it explicitly identifies the consumer
root file as onboarding and excludes `agent-framework/AGENTS.md` from normal
project onboarding.

## EA-AF-CONT-001

Requirements: `AF-CONT-001`
Method: `inspection`

Compare the standard runner inventory against `container/requirements.txt` and
the OS packages installed by `container/Dockerfile`; each runner dependency
must be provided by the base image.

## EA-AF-CONT-002

Requirements: `AF-CONT-002`
Method: `inspection`

Inspect `templates/rendered/Dockerfile.template` and verify it uses the selected
version's framework base image and installs only the consuming project's
package/runtime dependencies.

## EA-AF-BOOT-001

Requirements: `AF-BOOT-001`
Method: `automated-test`, `inspection`

Inspect the bootstrap skill and verify that it builds the framework image and
runs `python agent-framework/configure.py` inside Docker rather than invoking
host Python or host Bash. The scaffold test exercises `configure.py` as the
canonical configuration entry point.

## EA-AF-BOOT-002

Requirements: `AF-BOOT-002`
Method: `automated-test`, `inspection`

Inspect the bootstrap skill and verify it explicitly distinguishes unresolved
product decisions from bootstrap prerequisites and preserves unresolved choices
that are not needed to establish the repository.

## EA-AF-BOOT-003

Requirements: `AF-BOOT-003`
Method: `automated-test`, `inspection`

Inspect the bootstrap skill and human prompt and verify that the final bootstrap
report must contain feedback intended for the framework author.

## EA-AF-BOOT-004

Requirements: `AF-BOOT-004`
Method: `automated-test`, `inspection`

Inspect the bootstrap and contract-authoring skills and verify they instruct the
agent to preserve the developer's stated commitment boundary, avoid inventing
additional observable semantics, and keep independently violable obligations
under separate requirement IDs.

## EA-AF-BOOT-005

Requirements: `AF-BOOT-005`
Method: `automated-test`, `inspection`

Inspect the bootstrap skill and generated planning scaffold. Verify bootstrap
does not create product contracts, evaluation activities, roadmap commitments,
or an implementation milestone.

## EA-AF-BOOT-006

Requirements: `AF-BOOT-006`
Method: `automated-test`

Configure a temporary consuming project and verify its normalized metadata,
package, executable scaffold, smoke test, README, and architecture intent use
the supplied name and verbatim intent.

## EA-AF-BOOT-007

Requirements: `AF-BOOT-007`
Method: `automated-test`

Exercise valid normalization and names that normalize to an invalid identifier
or Python keyword. Verify invalid names fail before project files are written.

## EA-AF-BOOT-008

Requirements: `AF-BOOT-008`
Method: `automated-test`, `inspection`

Configure fixtures with the default and each supported Python version. Inspect
the rendered metadata and container build instructions and verify the base
Dockerfile accepts the matching build argument.

## EA-AF-BOOT-009

Requirements: `AF-BOOT-009`
Method: `automated-test`

Exercise missing, uninitialized or mismatched, clean, and locally modified
submodule states. Verify invalid registration fails and local dirtiness produces
a warning without preventing configuration.

## EA-AF-BOOT-010

Requirements: `AF-BOOT-010`
Method: `automated-test`

Exercise an unexpected root entry and entries matched by the template
`.gitignore`. Verify unexpected content fails without writes while ignored
content is preserved and reported.

## EA-AF-TOOL-001

Requirements: `AF-TOOL-001`
Method: `automated-test`

Load framework configuration for Python 3.12 and verify the framework resolves
Black's target spelling to `py312`. Inspect `run_black.py` to verify that target
is passed explicitly.

## EA-AF-TOOL-002

Requirements: `AF-TOOL-002`
Method: `inspection`

Inspect `run_ruff.py` and verify the framework extends Ruff ignores with
`EXE002`, documenting this as a cross-platform bind-mount accommodation rather
than a project-local Ruff configuration.

## EA-AF-TOOL-003

Requirements: `AF-TOOL-003`
Method: `automated-test`, `inspection`

Exercise the milestone-reference heuristic with direct `MS`, `Milestone N`, and
`mNNN.md` forms and verify they are detected while generic wording such as
`current milestone` is not. Inspect the sanitizer exit-status logic and verify
these findings remain advisory even in strict Unicode mode.

## EA-AF-TOOL-004

Requirements: `AF-TOOL-004`
Method: `automated-test`

Parse an evaluation activity that declares a `Method:` line containing `automated-test` and
the `Evidence:` value `planned` without any matching `@covers(...)` declaration. Verify
traceability validation succeeds and the generated evaluation status is
`PLANNED-AUTOMATED`.

## EA-AF-DOC-001

Requirements: `AF-DOC-001`
Method: `automated-test`, `inspection`

Inspect the project documentation templates and verify navigation is expressed
with ordinary repository-relative Markdown links and no Sphinx/MyST configuration
or toctree directives are seeded.

## EA-AF-SCAFF-001

Requirements: `AF-SCAFF-001`
Method: `inspection`

Inspect the seeded contract decorator and verify its intentional dynamic test
metadata assignment is locally justified/suppressed for Ruff while remaining
valid Python typing behavior for Pyright.

## EA-AF-DOC-002

Requirements: `AF-DOC-002`
Method: `automated-test`, `inspection`

Inspect the aggregate verification runner and documentation runners. Verify the
`docs` group invokes both Markdown linting and local-link validation, and verify
the link checker uses lychee offline so external network availability cannot
affect the documentation gate.

## EA-AF-REPO-001

Requirements: `AF-REPO-001`
Method: `automated-test`, `inspection`

Verify `.githooks/pre-commit` exists and invokes the complete framework
verification runner inside Docker. Verify `templates/` contains no Git hook and
that the repository documentation describes the one-time `core.hooksPath`
activation.
