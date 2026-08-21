# Project documentation

This directory is the project-owned source of truth. The reusable process for
working with it lives under `agent-framework/workflow/`.

## Core areas

- [Architecture](architecture/README.md) — system/module boundaries,
  responsibilities, structural decisions, and stable project model.
- [Contracts](contracts/README.md) — externally observable behavioral
  requirements and their evaluation activities.
- [Planning](planning/README.md) — mutable roadmap, executable milestones,
  handovers, reviews, and planning history. Planning is not authoritative over
  contracts/architecture.
- [Development](development/README.md) — project-specific development facts not
  already owned by the framework.

Create additional authoritative areas (for example a public protocol
specification) only when the project actually needs them.

Historical notes and implementation do not silently redefine an authoritative
contract. When authoritative sources conflict, surface and resolve the conflict
before implementing affected behavior.
