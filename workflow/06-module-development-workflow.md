# Module Development Workflow

## Purpose

This document defines the development workflow for modules whose behavior is
defined by an explicit specification or contract.

The workflow separates specification, evaluation design, executable evidence,
scaffolding, and implementation so that agents do not accidentally define
behavior through implementation or test choices.

## 1. Establish the authoritative specification

Before writing implementation code or contract tests:

1. Identify the authoritative specification.
2. Read the complete specification relevant to the module.
3. For behavioral contracts, read `docs/contracts/README.md`.
4. If the contract has an evaluation document under
   `docs/contracts/evaluation/`, read it completely.
5. Identify public interfaces and externally observable behavior.
6. Identify required success, failure, ordering, lifecycle, atomicity, and edge
   semantics.
7. When requirement IDs are available, use
   `docs/contracts/generated/requirements.csv` as a checklist. It is
   project-wide; filter it by `contract`.

The contract is authoritative. The evaluation activity is subordinate evidence
guidance. Implementation and existing tests are not authoritative behavior
sources.

If the specification or evaluation activity is ambiguous, contradictory, or
incomplete, do not silently invent behavior. Resolve the affected specification
before implementing it.

## 2. Check requirement quality before writing tests

Before converting requirements into tests, verify that each requirement ID
represents one independently assessable obligation.

A requirement is too broad when an implementation could satisfy one clause
while independently violating another and the requirement would therefore need
a partial verdict.

When a requirement is compound:

1. do not compensate with an overbroad test or `@covers(...)` declaration;
2. report the granularity issue;
3. normalize the contract before proceeding when the task permits contract
   changes.

Do not create executable coverage targets from application notes, examples,
caller guidance, or deliberate non-guarantees.

## 3. Design evidence from evaluation activities

For each applicable requirement, determine the required evidence from the
contract's evaluation document.

Evaluation methods may include:

- automated tests;
- public-interface/source inspection;
- analysis combining several observations.

For automated-test activities, identify before coding:

- setup;
- action;
- exact expected result;
- required failure state when applicable;
- ordering or invocation counts when applicable;
- state that must remain unchanged on failure;
- public exception type and fields when specified.

For callback tests, explicitly model registrations as `(registered_path,
callback)` pairs and determine:

- changed paths;
- applicable registrations;
- expected order;
- expected invocation count;
- expected `paths` payload.

## 4. Write behavioral tests before traceability metadata

Implement the behavioral tests first without using `@covers(...)` as a
checklist-completion mechanism.

Tests should:

- exercise public interfaces;
- verify required successful behavior;
- verify required failure behavior;
- inspect exact exceptions and public fields where specified;
- verify defensive-copy behavior by mutating returned objects;
- verify unregistration through a later observable operation;
- verify idempotence through invocation count or equivalent observation;
- verify ordering with exact sequence assertions;
- verify atomicity by examining state after failure;
- verify logging through an observable logger;
- verify lifecycle rules across multiple transactions when necessary;
- avoid depending on implementation details.

Executing an API is not enough to prove its semantics.

If a desired test cannot be justified by the contract and evaluation activity,
identify the missing or ambiguous requirement instead of silently expanding the
contract.

## 5. Add `@covers(...)` only after behavioral review

After the behavioral test suite exists, review it semantically and then add
traceability metadata.

For every proposed requirement ID on every test, ask:

> If this exact requirement were violated while the other relevant behavior
> remained correct, would this test fail?

If the answer is no, do not attach that ID.

Do not attach an ID merely because:

- the test calls the relevant API;
- the behavior is related;
- the implementation passes through relevant code;
- the requirement is a prerequisite for another assertion;
- the requirement is currently uncovered elsewhere.

A test may cover multiple requirements when one scenario independently proves
each of them. A requirement may need multiple tests or a parameterized test.

The traceability convention and tooling are defined in
`docs/contracts/README.md`.

## 6. Generate and review traceability

Run:

```text
python agent-framework/tools/contracts/generate_traceability.py
```

Inspect:

```text
docs/contracts/generated/requirements.csv
docs/contracts/generated/traceability.csv
```

Filter the project-wide artifacts by the applicable `contract` value.

Review every `PLANNED-AUTOMATED`, `MANUAL-REVIEW`, `MISSING-EVALUATION`, or `MISSING-AUTOMATED-EVIDENCE` requirement before adding more tests:

- deliberately planned automated evidence whose implementation milestone is still pending;
- deliberate inspection/analysis requirement requiring manual review;
- genuine missing automated evidence;
- missing or incomplete evaluation activity;
- contract ambiguity;
- compound requirement needing normalization.

Do not force every row green by weakening traceability semantics.

Then run:

```text
python agent-framework/tools/contracts/generate_traceability.py --check
```

## 7. Create the minimum scaffold

If tests cannot be collected because the implementation module or required
public symbols do not yet exist, create only the minimum scaffold required for
collection.

The scaffold may contain required modules, classes, functions, exception types,
public constants, and signatures. It must not implement requested behavior.

Do not use scaffolding to add validation, persistence, convenience behavior, or
speculative abstractions.

## 8. Verify the test setup

Run the relevant tests after creating the scaffold.

Expected state before implementation:

- collection succeeds;
- imports succeed;
- tests execute;
- `@covers(...)` declarations are structurally parseable;
- behavioral tests fail for behavior that has not yet been implemented.

Fix collection/scaffold problems before implementation work hides them.

## 9. Implement incrementally

For each logical increment:

1. identify the applicable contract requirements;
2. read their evaluation activities;
3. implement only the required behavior;
4. run relevant tests;
5. inspect failures;
6. correct implementation;
7. continue until the evidence passes.

Do not introduce public behavior merely because it seems useful.

## 10. Preserve contract authority

Do not allow implementation convenience to redefine the contract.

If implementation reveals behavior the contract does not define:

1. stop the affected behavior decision;
2. identify the missing decision;
3. update/resolve the contract deliberately;
4. update its evaluation activity;
5. update tests;
6. continue implementation.

## 11. Do not weaken evidence to match implementation

When a contract test fails, determine whether:

- implementation violates the contract;
- the test violates the contract/evaluation activity;
- the evaluation activity is inadequate;
- or the contract is incomplete/incorrect.

Do not change a test merely because the current implementation makes the test
inconvenient.

## 12. Final review

After relevant tests pass:

- compare implementation against the complete contract;
- compare tests with the evaluation activities;
- regenerate/check requirement and traceability CSVs;
- inspect every remaining `PLANNED-AUTOMATED`, `MANUAL-REVIEW`, `MISSING-EVALUATION`, or `MISSING-AUTOMATED-EVIDENCE` requirement;
- do not complete a milestone while requirements assigned to that milestone remain `PLANNED-AUTOMATED`;
- review every broad `@covers(...)` declaration for overclaiming;
- identify behavior not represented by the intended public contract;
- remove obsolete scaffolding and unused abstractions;
- verify failure paths and edge cases;
- run complete repository verification.

Passing tests and a green traceability matrix are necessary evidence but do not
by themselves prove complete specification conformance.

## Workflow summary

```text
Authoritative contract
        ↓
Requirement-quality review
        ↓
Evaluation activities
        ↓
Behavioral tests (without coverage pressure)
        ↓
Semantic test review
        ↓
@covers(...) assignment
        ↓
Traceability generation and review
        ↓
Minimal scaffold
        ↓
Incremental implementation
        ↓
Contract/evaluation review
        ↓
Complete verification
```

## Guiding principle

**The contract defines behavior.**

**Evaluation activities define suitable evidence.**

**Tests provide executable evidence.**

**Traceability connects evidence to independently assessable requirements.**

**Implementation satisfies the contract.**
