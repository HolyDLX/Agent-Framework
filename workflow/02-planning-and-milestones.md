# Planning and Milestones

## Purpose

This document defines how an agent works with the project's planning and
milestone system.

The planning structure and the meaning of its documents are defined in
[Project planning](../docs/planning/README.md).

## Before starting a milestone

Before implementing a milestone:

1. Read `docs/planning/README.md`.
2. Read `docs/planning/roadmap.md`.
3. Identify the milestone marked `Current`.
4. Read the current milestone document under `docs/planning/milestones/`.
5. Read the authoritative project documentation relevant to the milestone.
6. Inspect the current implementation and tests relevant to the milestone.

Topic documents and historical artifacts are not part of the default reading
set. Read them when they are relevant to the current work.

Do not use historical handovers, reviews, notes, or legacy roadmap snapshots as
a substitute for the current roadmap or authoritative project documentation.

## Milestone scope

The current milestone defines the work to be performed.

Implement the milestone in its defined order.

Do not silently:

- implement work belonging to later milestones;
- expand the milestone because related improvements appear useful;
- change public behavior that is not required by the milestone;
- turn an implementation discovery into a new requirement.

If the milestone is incomplete, contradictory, or no longer appropriate,
identify the problem before implementing affected work.

## Planning changes

The roadmap is intentionally mutable. Accepted/current milestone entries should
link to their `docs/planning/milestones/mNNN.md` document with ordinary Markdown
links so local documentation verification checks those navigation targets.

Implementation and review may reveal that planned work needs to change. When a
significant planning problem is discovered:

1. identify the problem;
2. determine what work is actually required;
3. update `docs/planning/roadmap.md`;
4. create, split, remove, or reorder milestones as necessary;
5. preserve completed milestone history.

Milestone identifiers are permanent. Their identifiers do not represent their
current position in the roadmap.

For example, a newly created `MS18` may be inserted before an already planned
`MS16` when that ordering better reflects the required work. Neither milestone
is renumbered.

## Future planning and topics

Use `docs/planning/topics/` for future-oriented thoughts that are not yet
ready to become executable milestones.

When asked to distill a topic into milestones, organize the recorded thoughts
into coherent candidate work packages. Preserve unresolved questions and do not
invent decisions merely to make the plan complete.

Candidate milestone proposals are working output. Do not create milestone files
or add them to the roadmap until the proposed work has been accepted.

## Implementation items

Work through the implementation items defined by the current milestone.

Before marking an item complete:

- implement the required behavior;
- add or update the required tests;
- when the work is governed by a contract that uses requirement traceability,
  update the applicable `@covers(...)` declarations and regenerate/check the
  contract traceability artifacts;
- update required documentation;
- perform the applicable verification;
- confirm that the implementation satisfies the milestone's completion
  criteria.

Do not mark an item complete merely because the corresponding code exists.

If an item cannot be completed as specified, leave it incomplete and record the
reason.

## Working notes

Use the milestone's companion `-notes.md` file for implementation working notes
when useful.

Notes may contain observations, discoveries, temporary reasoning, hypotheses,
unresolved questions, and information useful during the current implementation.

Notes are non-authoritative. When a discovery becomes permanent project
knowledge, document it in the appropriate authoritative documentation.

## Handover

At the end of milestone implementation, create or update the milestone's
`-handover.md` file according to the planning workflow.

The handover should preserve useful historical context such as implementation
state, discoveries, changed assumptions, unresolved concerns, known
limitations, verification results, and recommendations.

A handover is historical documentation, not the authoritative source for the
current project state.

## Review

The following agent is responsible for reviewing the previous milestone. The
review belongs in the milestone's `-review.md` companion file.

The review should independently assess the resulting implementation against:

- the milestone goal and scope;
- completion criteria;
- applicable project contracts and specifications;
- relevant architecture;
- tests and verification.

Do not rewrite the original milestone or handover to make the historical record
appear more accurate in hindsight.

If the review identifies larger issues, update the roadmap so the required
follow-up work is explicitly planned.

## Historical planning documents

Completed milestone documents, notes, reviews, handovers, and legacy roadmap
snapshots are retained as historical records.

They describe what was planned, discovered, implemented, or believed at a
particular point in time. Do not rewrite historical documents merely because
the project's current understanding has changed.

The current roadmap and authoritative project documentation define the current
state; historical planning documents explain how that state was reached.
