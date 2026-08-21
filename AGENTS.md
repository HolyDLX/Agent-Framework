# Agent Framework development instructions

This file applies when developing the **agent-framework repository itself**.
It is not the onboarding file for agents working on a consuming project.

Before changing the framework:

1. Read every document under `workflow/`.
2. Read `docs/README.md` and the relevant framework-owned documentation.
3. Read `docs/planning/roadmap.md` and the current milestone when one exists.
4. Inspect affected tools, templates, skills, and tests.
5. Check `git status` and preserve unrelated changes.

The framework dogfoods its own workflow. Its own project documentation lives
under `docs/`; reusable consumer-facing process lives under `workflow/` and
`skills/`. Human-facing copy-ready entry prompts live under `human/` and must
remain thin pointers to canonical skills rather than duplicate workflow rules.

When changing behavior exposed to consuming projects, update the framework
contract/evaluation documentation before implementation where applicable.

Do not modify a parent consuming repository when working on this repository as
a submodule unless that parent-project change is explicitly requested.

The framework repository uses `.githooks/pre-commit` as a repository-only final
commit gate. Each checkout should configure `git config core.hooksPath .githooks`.
Do not copy or install this hook into consuming projects.
