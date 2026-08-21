# Agent instructions

This repository uses the reusable development framework under
`agent-framework/`.

Before substantial project work:

1. Read `agent-framework/workflow/README.md` and every workflow document it
   requires.
2. Read `docs/README.md`.
3. Read the project-specific documentation relevant to the task.
4. Use the applicable canonical skill under `agent-framework/skills/` when one
   matches the task.

The framework defines **how work is performed**. Project-owned documentation
defines **what this project is and what it must do**.

`agent-framework/AGENTS.md` is for development of the framework submodule
itself. Do not use it as project onboarding unless the task explicitly modifies
the framework.

If project needs expose a missing framework capability, surface the gap. Prefer
adding a supported framework configuration point or reusable tool change over
creating an ad-hoc project-local fork of the standard engineering toolchain.
