# Review and Handover

## Purpose

This document defines the agent workflow for reviewing completed milestone
work and handing work between agents.

The planning structure and the meaning of milestone documents are defined in
[Project planning](../docs/planning/README.md).

## Milestone completion

When the implementation work for a milestone is complete:

1. Complete the required implementation work.
2. Run the required verification.
3. Confirm the milestone's completion criteria.
4. Record relevant implementation information in the milestone's `-notes.md`
   companion file.
5. Create or update the milestone's `-handover.md` companion file.
6. Leave the milestone in a state that can be independently reviewed.

Do not declare a milestone complete merely because its implementation items
have been checked off.

## Handover

The implementation agent writes the milestone handover.

The handover is a permanent historical document. It records what the agent
considered important at the time the milestone was completed.

A handover may contain:

- the resulting implementation state;
- important implementation discoveries;
- changed assumptions;
- unresolved concerns;
- known limitations;
- relevant verification results;
- recommendations for the next agent;
- information that may help explain decisions made during the milestone.

The handover should be useful to a future developer trying to understand how
the project evolved.

It does not need to reproduce the milestone specification or other
authoritative documentation.

It must not claim that unresolved work is complete.

## Historical status of handovers

A handover describes the state and understanding of the project at a
particular point in time.

After the milestone has passed, it is historical documentation.

Do not treat an old handover as:

- current instructions;
- the current project state;
- an authoritative specification;
- an authoritative API contract;
- an authoritative architecture document;
- an authoritative protocol contract.

The current agent planning roadmap and current authoritative project
documentation take precedence.

Historical handovers may be consulted when investigating why a decision was
made or how the implementation evolved.

## Review

The next agent is responsible for reviewing the completed milestone.

The review is an independent assessment of the milestone's resulting state.

Create:

```text
<milestone>-review.md
```

The review should assess the implementation against:

- the milestone goal;
- the defined scope;
- the completion criteria;
- applicable project specifications and contracts;
- applicable contract evaluation activities under `docs/contracts/evaluation/`;
- relevant architecture;
- tests and other required evaluation evidence;
- contract traceability artifacts when the applicable contracts use
  requirement IDs;
- verification results;
- and the actual resulting implementation.

The review should distinguish between:

- confirmed defects;
- missing requirements;
- specification gaps;
- implementation risks;
- accepted limitations;
- observations that require no action.

Do not assume that a completed implementation item or passing verification
means that the milestone is correct.

When contract traceability is available:

- inspect every requirement reported as `MANUAL-REVIEW`, `MISSING-EVALUATION`, or `MISSING-AUTOMATED-EVIDENCE`;
- compare the evidence with the applicable evaluation activity;
- verify that tests claiming `@covers(...)` actually exercise the cited
  requirement;
- apply the counterfactual: if the requirement were violated while related
  behavior remained correct, would the test fail?;
- identify stale, overly broad, or incorrect coverage declarations;
- identify requirements that are still too compound to receive an independent
  verdict; and
- treat traceability as a completeness aid rather than as proof of behavioral
  correctness.

## Review findings

If the review finds only minor issues that can be addressed within the
existing milestone scope, they may be documented for correction according to
the current workflow.

If the review finds larger issues, do not silently expand the implementation
scope.

Instead:

1. document the findings in `<milestone>-review.md`;
2. determine what follow-up work is required;
3. update `docs/planning/roadmap.md`;
4. add, split, remove, reorder, or otherwise modify milestones as necessary;
5. ensure the required follow-up work has an explicit milestone.

The roadmap is intentionally mutable.

Milestone identifiers are permanent and must not be renumbered merely because
the roadmap changes.

## Do not rewrite history

Do not rewrite a completed milestone, handover, or review merely to make the
historical record agree with the project's current understanding.

If a later review reveals that an earlier decision was wrong, preserve the
original record and document the corrected understanding in the appropriate
current project documentation.

The history should make it possible to see how the project and development
process evolved over time.

## Handover quality

A handover is not a second milestone specification.

Do not spend unnecessary effort reproducing information that is already
available in authoritative project documentation.

The value of a handover is the information that would otherwise be difficult
for the next agent to recover:

- what actually happened;
- what was discovered;
- what changed;
- what remains uncertain;
- what deserves attention.

Handover quality should improve as the development workflow improves.

## Review quality

A review should not merely confirm that the milestone was completed.

Look for discrepancies between:

- the intended behavior and the actual behavior;
- the contract and the implementation;
- the milestone scope and the changes made;
- the stated verification and the actual verification;
- the architectural intent and the resulting design.

The review should prioritize actionable findings over commentary.

## Historical documents and the current workflow

Historical notes, handovers, and reviews are retained because they provide
development history.

They are not part of the default current workflow unless the current task
requires historical investigation.

The current agent should start from:

1. the current agent instructions;
2. the current planning roadmap;
3. the current milestone;
4. current authoritative project documentation.

Only consult historical milestone documents when they provide information
needed for the current task.
