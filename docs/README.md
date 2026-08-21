# Agent Framework documentation

This directory contains project-owned documentation for developing the
framework itself. It is distinct from the reusable workflow under `workflow/`
and the project skeletons under `templates/`.

Authority for framework development, highest to lowest when applicable:

1. explicit user instruction for the current task;
2. framework contracts under `docs/contracts/`;
3. framework architecture under `docs/architecture/`;
4. current accepted milestone under `docs/planning/`;
5. implementation and tests as evidence of current state, not as authority over
   a conflicting contract.

Reusable consumer-project process belongs in `workflow/` or `skills/`, not in
this directory.

## Documentation areas

- [Architecture](architecture/README.md)
- [Development](development/README.md)
- [Contracts](contracts/README.md)
- [Planning](planning/README.md)
