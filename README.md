# Agent Framework

A reusable, opinionated framework for agent-driven Python development.

The framework owns **how development is performed**: onboarding, planning,
contracts, evaluation activities, implementation discipline, verification,
review, reusable agent skills, the standard Python verification toolchain, and
the controlled development container.

A consuming project owns **what is being built**: project goals, architecture,
contracts, evaluation definitions, roadmap, milestones, source code, tests, and
project-specific utilities.

## Add to a new repository

From an empty Git repository:

```text
git submodule add <agent-framework-repository-url> agent-framework
git add .gitmodules agent-framework
git commit -m "chore: add agent framework"
```

Then instruct the agent:

```text
Read agent-framework/skills/bootstrap-project/SKILL.md and bootstrap this
repository. The initial project intent is: <intent>.
```

Committing the submodule addition first is recommended but not required by the
configuration tool. The bootstrap skill builds the framework base image first
and runs `python agent-framework/configure.py` inside Docker. Host Bash, WSL,
and host Python are therefore not bootstrap prerequisites. Bootstrap creates an
empty planning/specification structure and stops before product specification,
milestone planning, or feature implementation.

Reusable skills include bootstrap, contract authoring, milestone implementation,
focused change verification, and independent milestone review. Copy-ready
developer entry prompts and their prerequisites live under `human/`. During normal
development, `verify-change` provides the focused test/check loop while the
workflow still requires complete verification before handover.

## Repository boundary

```text
consumer-project/
├── AGENTS.md                         project agent entry point
├── agent-framework/                  pinned framework submodule
├── .agents/skills/                   thin discovery wrappers
├── agent-framework.toml              supported project inputs to the framework
├── toolctl.py                         thin tool-management wrapper
├── run_verification.py                thin verification wrapper
├── Dockerfile                        project image FROM framework base
├── docs/                             project-owned truth
├── src/                              project source
├── tests/                            project tests
└── tools/                            project-specific utilities only
```

The framework submodule contains its own `AGENTS.md`. That file governs work on
the framework itself. A normal consuming-project agent must not use it as the
project onboarding document; the consumer project's root `AGENTS.md` is the
entry point.

## Verification

The framework provides the standard toolchain and its dependencies. Consuming
projects do not copy the runners.

The framework base image contains the dependencies required by every framework
runner. The project Dockerfile builds a thin project image on top and installs
project runtime/package dependencies.

On hosts with only Git and Docker, run framework verification directly inside
the project development image:

```text
docker run --rm --mount type=bind,source=<project-root>,target=/workspace --workdir /workspace <project-development-image> python run_verification.py
```

When host Python is intentionally available, the framework also provides the
convenience dispatcher:

```text
python run_verification.py --container
```

Focused runs append a configured category such as `code`, `documentation`,
`tests`, `contracts`, or `repository` to the verification command.

The `documentation` category lints Markdown and validates repository-local
Markdown links offline. Documentation navigation uses ordinary Markdown links;
Sphinx/MyST is not part of the framework toolchain.

## Framework repository pre-commit gate

The Agent Framework repository itself ships a repository-only Git hook under
`.githooks/pre-commit`. It builds the controlled framework images and runs the
complete verification suite before a commit is accepted. The hook is not part
of `templates/` and is therefore not installed into consuming projects.

Enable it once per framework checkout:

```text
git config core.hooksPath .githooks
```

The hook requires Git and a running Docker service. It does not require host
Python.

## Framework evolution

Projects pin the framework through the Git submodule commit. Workflow, skills,
runners, container tooling, and supported configuration are improved in this
repository and adopted by consuming projects when their submodule pointer is
updated.

Files copied or rendered from `templates/` are project-owned seeds after
configuration. Updating the submodule never modifies them. Migration and
reconfiguration of an existing project are not currently supported.

## Supported environment

The controlled development image is version-constrained rather than
byte-for-byte reproducible. Bootstrap supports Python 3.12 and 3.14 and defaults
to 3.12. Docker hosts are currently limited to x86-64. Windows with Docker
Desktop is the primary tested bootstrap host; Linux commands map the host UID
and GID to avoid root-owned bind-mount files. Verification is local-only; the
repository does not currently provide CI.

## License

Agent Framework is licensed under the Apache License 2.0. Files copied or
generated into a consuming project receive the additional permissions in
[`TEMPLATE_EXCEPTION.md`](TEMPLATE_EXCEPTION.md).
