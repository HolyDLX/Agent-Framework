# Implementation

## Purpose

This document defines the general rules agents must follow while implementing
changes.

Detailed planning is defined in `02-planning-and-milestones.md`.

The specification-to-test-to-implementation workflow for individual modules is
defined in `06-module-development-workflow.md`.

## Implement the requested behavior

Implement the behavior required by the applicable specification and current
scope.

Do not:

- invent unspecified public behavior;
- implement speculative features;
- expand the scope because related improvements appear useful;
- silently change existing public behavior;
- implement work belonging to a later milestone.

When the specification does not define required behavior, stop and resolve the
missing decision rather than making the implementation choice part of the
contract by accident.

## Keep changes focused

Make the smallest coherent change that satisfies the requested behavior.

Do not perform unrelated:

- refactoring;
- cleanup;
- modernization;
- dependency changes;
- formatting changes;
- renaming;
- architectural changes.

If unrelated problems are discovered, record them for the appropriate planning
or review workflow instead of silently addressing them.

A refactoring is appropriate when it is necessary to implement the requested
behavior safely or when the current milestone explicitly includes it.

## Preserve existing behavior

Unless a change is explicitly required:

- preserve existing public APIs;
- preserve existing behavior;
- preserve compatibility;
- avoid unnecessary changes to serialization, configuration, or persistence
  formats.

When intentional behavior changes are required, ensure that the applicable
specification, tests, traceability metadata and generated artifacts where
applicable, and documentation are updated consistently.

## Tests

Changes to behavior must have appropriate test coverage.

Tests should verify the behavior required by the applicable specification and
should not merely verify that a particular implementation was used.

When the applicable behavioral contract uses requirement IDs, contract tests
must declare the requirements they verify through the project's contract
traceability mechanism. The conventions and generated artifacts are defined in
`docs/contracts/README.md`.

A declared `@covers(...)` relationship is a traceability claim, not proof that
the test adequately verifies the cited requirement.

When a change crosses module, process, transport, installation, or tooling
boundaries, use the appropriate integration or end-to-end tests rather than
relying exclusively on unit tests.

Do not weaken or remove tests merely to make an implementation pass.

During implementation, use `agent-framework/skills/verify-change/SKILL.md` to
select focused tests and verification groups, diagnose failures, and widen the
verification scope as each implementation slice stabilizes. Focused checks do
not replace the complete verification gate required before handover.

If a test conflicts with the specification, determine whether the test or the
specification is wrong before changing either.

## Public interfaces

Treat public interfaces as contracts.

Do not add public parameters, methods, attributes, return values, exceptions,
configuration options, or other externally observable behavior unless they
are required by the applicable specification.

Avoid exposing internal implementation details through public interfaces.

When a required change affects a public interface:

1. update or establish the applicable behavioral contract in `docs/contracts/`
   when externally observable behavior changes;
2. update the contract tests;
3. implement the change;
4. update the public Python docstrings so the source-level interface documentation
   reflects the interface;
5. update any relevant Markdown user, protocol, architecture, interface, or
   development documentation.

Source docstrings and interface documentation describe the public Python
interface. They do not replace the authoritative behavioral contract.

## Ownership and lifecycle

Make ownership and lifecycle explicit when changing stateful components.

Consider:

- who creates an object;
- who owns it;
- who may modify it;
- when ownership changes;
- what happens during shutdown;
- what happens after failure;
- whether cleanup is guaranteed;
- whether concurrent access is possible.

Do not introduce shared mutable state merely because it is convenient.

When the specification requires atomicity, rollback, isolation, or concurrency
behavior, test those guarantees explicitly.

## Dependencies

Do not add or change dependencies without a concrete requirement.

Before adding a dependency, consider:

- whether existing functionality already provides what is needed;
- whether the dependency is required at runtime or only during development;
- whether it affects supported environments;
- whether packaging and verification need to be updated.

## Documentation

Update project documentation when implementation changes:

- public behavior;
- public interfaces;
- architecture;
- protocol behavior;
- configuration;
- development workflows;
- or other documented guarantees.

Behavioral guarantees belong in `docs/contracts/`.

Public Python signatures and interface descriptions belong in source docstrings.
Project-facing interface documentation that must be navigable outside the source
belongs in the appropriate Markdown documentation area.

Permanent project knowledge must be placed in the appropriate documentation
area. Do not leave important decisions only in agent notes, milestone notes,
or handovers.

## Destructive operations

Do not perform destructive operations without verifying their scope.

This includes:

- deleting files;
- overwriting unrelated changes;
- resetting the working tree;
- rewriting history;
- removing dependencies;
- changing persistent data formats.

Existing user changes must be preserved unless the user explicitly requests
otherwise.

## Commit boundaries

Do not create commits unless the user explicitly asks for them or the active
workflow requires them.

When a commit is required, follow the repository's commit conventions and
ensure that the commit contains only the intended changes.
