# Scope and Onboarding

## Purpose

This document defines the repository-wide onboarding and scope rules for
agents.

User instructions for the current task always take precedence.

## Before changing files

Before making changes:

- Read the files explicitly named by the user.
- Read the repository's top-level `README.md`.
- Identify the current milestone and read its milestone document when the task
  is part of milestone work.
- Read the relevant architecture, contracts, interface, protocol, and
  development documentation for the requested work.
- When work is governed by a behavioral contract, also read
  `docs/contracts/README.md` for the repository's contract conventions and
  traceability rules.
- Inspect the relevant source code and tests.
- Check recent changes when they are relevant to understanding the current
  state.
- Check `git status` before editing.

Existing uncommitted changes belong to the user. Do not overwrite, reset,
discard, or otherwise modify unrelated existing changes without explicit
permission.

Separate requested work from unrelated work already present in the tree.

## Establish the applicable specification

Before implementing behavior, identify the authoritative specification for the
work.

Depending on the task, this may be:

- a behavioral contract in `docs/contracts/`;
- an architecture document;
- a protocol contract;
- a milestone specification;
- a module-specific specification;
- source documentation explicitly designated as authoritative;
- or another explicitly designated source.

Source docstrings and interface documentation describe public Python interfaces.
They must not be treated as a substitute for an authoritative behavioral
contract when one exists.

Do not treat implementation details, old planning notes, agent notes, or
historical handovers as authoritative merely because they contain a detailed
description.

If multiple authoritative documents appear to conflict, do not silently
choose one. Identify the conflict and resolve it before implementing the
affected behavior.

## Scope

Work only within the requested scope.

Do not expand a task because related improvements appear useful.

If implementation reveals work outside the current scope:

- record it as appropriate for the current planning or review workflow;
- report it to the user when it affects the requested outcome;
- do not silently implement it.

For milestone work, follow the current milestone and its implementation order.
Do not silently implement later milestone work.

For focused bug fixes or small changes, use a proportionate scope rather than
inventing milestone work.

## Clarification

Ask the user for clarification when an instruction is materially unclear and
different interpretations would change:

- implementation behavior;
- scope;
- public API;
- data;
- architecture;
- protocol behavior;
- or commit history.

Make reasonable assumptions only for minor details that do not materially
change the requested outcome.

## Preserve user changes

Before editing:

```text
git status
```

Use the result to identify changes that already exist.

Do not:

- reset the working tree;
- restore unrelated files;
- overwrite unrelated modifications;
- rewrite history;
- or otherwise discard user work

without explicit permission.

## Onboarding completion

After completing onboarding, briefly report the result to the user.

If no issues were found, keep the response short.

If there are issues, report the issues without unnecessary detail. The user can
ask for further analysis.
