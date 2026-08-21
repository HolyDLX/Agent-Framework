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

The framework is opinionated. Standard verification behavior is framework
owned. Project differences are expressed only through supported fields in
`agent-framework.toml`. When a legitimate project need is not representable,
the preferred change is to extend the framework configuration model rather than
fork the runner/tool configuration in the consuming project.
