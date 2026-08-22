# Framework architecture

## Boundary

Agent Framework is a reusable Git repository intended to be included in Python
projects as a visible `agent-framework/` submodule.

The framework owns:

- reusable agent workflow and skills;
- project bootstrap templates and mechanical initialization;
- the standard Python verification runners and their policy;
- contract/traceability mechanics;
- the base development container and all dependencies required by framework
  tools;
- supported configuration semantics exposed through `agent-framework.toml`.

A consuming project owns:

- project purpose and product decisions;
- project architecture/contracts/evaluation activities;
- roadmap, milestones, handovers, and reviews;
- source and tests;
- runtime/package dependencies;
- genuinely project-specific utilities.

## Container model

`container/Dockerfile` builds the framework base image. A consuming project uses
the seeded root `Dockerfile`, whose base is that framework image. The framework
Docker helper ensures the base image exists before building the project image.

`/workspace` is reserved for the consuming project. Framework runtime assets
are available through the project's `agent-framework/` checkout; the base image
does not treat `/workspace` as framework-owned state.

## Configuration model

The framework owns category and tool bundle implementations. Categories and
tools are discovered from validated TOML manifests; consuming projects select
ordered tool assignments in the machine-managed `[tools.*]` section of
`agent-framework.toml`. The project-local `toolctl.py` and
`run_verification.py` files are thin forwarding wrappers.

Bundle defaults apply only when no corresponding project-local tool
configuration exists. Deployed local defaults become project-owned and replace
the bundle configuration as a whole. Framework updates never overwrite them
without an explicit `reset-defaults --force` command.

Bootstrap profiles select the project skeleton and initial tool assignments.
The initial `generic` profile is explicit and creates the minimal executable
Python scaffold.
