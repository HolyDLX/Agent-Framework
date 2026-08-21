# Verification

## Command execution on Docker-only hosts

The Python commands in this workflow are convenience dispatchers when host
Python is intentionally available. Host Python is **not** a framework
prerequisite. On a Docker-only host, run the same framework runner inside the
already-built project development image and omit `--container`, for example:

```text
docker run --rm --mount type=bind,source=<project-root>,target=/workspace --workdir /workspace <project-development-image> python agent-framework/tools/run_verification.py
```

Use the host-appropriate mount spelling. Verification semantics are defined by
the framework runner executed inside the container, not by the host launcher.

## Development container

At the start of milestone work, run:

```text
python agent-framework/tools/container/docker_helper.py --build-if-missing
```

Run it once per milestone start, not before every edit.

It checks Docker availability and reuses the development image when present,
building it only when missing.

Use `--rebuild` only when the user requests a fresh image or Docker state must
be diagnosed.

If Docker is unavailable, stop the milestone workflow.

Do not substitute host tests for the required verification.

## Required verification

The required default verification command is:

```text
python agent-framework/tools/run_verification.py --container
```

Verification scripts may take longer than other repository instructions,
especially when they build or run checks in the development container.

It runs the complete source verification workflow in the development
container, including formatting, linting, documentation, typing, tests, coverage,
contract traceability, repository-file checks, and sanitizer checks.

The AI sanitizer also emits advisory `REVIEW` findings for possible direct
milestone references outside `docs/planning/`. These findings do not fail the
gate automatically because false positives are possible. The agent must inspect
each reported file/line and remove or relocate confirmed direct milestone
references; false positives may remain with an explicit review conclusion.

Run it after implementation and before marking an implementation item
complete.

A passing set of individual verification commands does not replace the
combined verification result.

## Diagnostic runners

Use individual runners with `--container` when diagnosing or reproducing a
specific failing verification gate.

Available diagnostic runners include:

```text
python agent-framework/tools/run_black.py --container
python agent-framework/tools/run_ruff.py --container
python agent-framework/tools/run_pydoclint.py --container
python agent-framework/tools/run_ai_sanitizer.py --container
python agent-framework/tools/run_pyright.py --container
python agent-framework/tools/run_pytest.py --container
python agent-framework/tools/run_coverage.py --container
python agent-framework/tools/run_markdownlint.py --container
python agent-framework/tools/run_linkcheck.py --container
```

After making a diagnostic fix, rerun the combined verification:

```text
python agent-framework/tools/run_verification.py --container
```

A set of passing individual runners does not replace the combined result.

## Contract evaluation and traceability

When a task changes a current behavioral contract, read the corresponding
evaluation document under `docs/contracts/evaluation/` before judging test
adequacy. The contract defines required behavior; the evaluation document
defines suitable evidence.

When a task changes a behavioral contract that uses requirement IDs, or changes
contract tests that declare requirement coverage, verify the generated contract
traceability artifacts with:

```text
python agent-framework/tools/contracts/generate_traceability.py --check
```

Run the generator without `--check` first when the authoritative contract or
coverage declarations intentionally changed and the generated CSV artifacts
therefore need to be updated.

The canonical generated artifacts are:

```text
docs/contracts/generated/requirements.csv
docs/contracts/generated/traceability.csv
```

They are project-wide files. Use their `contract` column when inspecting one
specific contract. Do not edit either CSV manually.

Contract traceability is part of the aggregate `contracts` verification group.
The direct generator command remains useful when intentionally regenerating artifacts.

A passing traceability check establishes only structural consistency and
freshness. It does **not** establish that a test adequately verifies every
requirement it claims to cover.

For semantic review, apply the evaluation activity and this counterfactual to
every claimed requirement:

> If this exact requirement were violated while the other relevant behavior
> remained correct, would this test fail?

If the answer is no, the `@covers(...)` declaration is incorrect even when the
generated traceability matrix reports `AUTOMATED` or `MIXED`. A
`PLANNED-AUTOMATED` row is valid before its responsible implementation work, but
it must not be treated as completed evidence.

## Focused verification

The aggregate runner supports focused verification groups.

For example:

```text
python agent-framework/tools/run_verification.py --container docs
python agent-framework/tools/run_verification.py --container code
python agent-framework/tools/run_verification.py --container testing
python agent-framework/tools/run_verification.py --container contracts
python agent-framework/tools/run_verification.py --container repository
```

Use focused verification when diagnosing a specific area.

Focused verification does not replace the complete verification required before
milestone completion.

## Host environment

Host-environment verification is diagnostic only.

Do not use host results as a substitute for container verification unless the
user explicitly requests host testing.

## Verification evidence

Do not claim that verification was performed unless it was actually run.

When reporting completed work, state:

- which verification was run;
- whether it passed;
- any relevant limitations;
- any checks that were intentionally not run.

## Tool documentation

The `agent-framework/tools/README.md` documentation describes the available development and verification
tools.

This document defines the **agent's obligation to use them**.

If the tool documentation and this workflow appear to disagree about whether
an agent must perform a verification step, identify the conflict rather than
silently choosing an interpretation.
