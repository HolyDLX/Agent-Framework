# Project planning

This directory provides persistent planning context so a fresh agent can
understand what is current, what is planned, and what previous implementation
or review discovered without reconstructing state from chat history.

Planning is human-readable but is **not authoritative project behavior**.
Permanent project truth belongs in architecture, contracts, or another
explicitly authoritative specification area.

## Structure

```text
docs/planning/
├── README.md
├── roadmap.md
├── topics/
├── milestones/
│   ├── m001.md
│   ├── m001-handover.md
│   ├── m001-review.md
│   └── ...
└── history/
```

Only create notes, review, or handover companions when they contain useful
information.

## Roadmap

`roadmap.md` is the canonical registry and current ordering of accepted
milestones. Milestone row order represents intended execution order; milestone
numbers are permanent identities, not ordering keys.

## Milestones

A milestone is a bounded executable work package ready to hand to an
implementation agent. It should normally define:

- objective;
- scope and exclusions;
- implementation work;
- dependencies/prerequisites;
- authoritative documentation governing the work;
- verification/completion expectations.

Files use zero-padded permanent identifiers (`MS7` -> `m007.md`). Never
renumber historical milestones merely because roadmap order changes.

## Topics

Use `topics/` for future ideas not ready to become accepted executable work.
Topics may be speculative and incomplete. Distilling topics into proposed
milestones does not authorize missing product or architecture decisions.

## History

Completed milestone documents, handovers, reviews, notes, and old roadmap
snapshots are historical. Do not rewrite them to agree with later decisions.
Current authoritative project documentation and the current roadmap define the
present state.

## Planning navigation

- [Roadmap](roadmap.md)
- [Milestones](milestones/README.md)
- [Topics](topics/README.md)
- [History](history/README.md)
