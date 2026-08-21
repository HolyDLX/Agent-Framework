# Contracts

This directory contains authoritative externally observable behavioral
contracts for the project.

Contracts define **what must be true**. They do not define unnecessary
implementation mechanics. Implementation, tests, planning, evaluation
activities, generated CSV files, and historical notes must not silently
redefine a conflicting contract.

The documentation model deliberately separates:

- **requirements** — independently assessable obligations;
- **application notes** — authoritative guidance, examples, rationale, and
  deliberate non-guarantees without independent coverage targets;
- **evaluation activities** — suitable evidence for deciding whether a
  requirement is satisfied.

This is a lightweight evaluation-oriented structure inspired by useful Common
Criteria specification practices without adopting certification bureaucracy.

## Requirement quality

A requirement ID identifies one independently assessable obligation.

Use the following test when deciding whether to split a statement:

> Could one implementation satisfy one clause while independently violating
> another clause?

If yes, the clauses should normally receive separate requirement IDs.

A coherent lookup table or exhaustive parameterized rule may remain one
requirement when it can receive one meaningful satisfied/not-satisfied verdict.

Do not assign IDs to prose merely because it contains normative language.

## Requirement declarations

Use a stable machine-parseable declaration:

```markdown
**MOD-AREA-001** — The externally observable requirement text.
Type: `behavioral`
```

The declaration starts with a bold ID, followed by an em dash and requirement
text. Wrapped continuation lines belong to the same requirement paragraph. The
final line declares exactly one requirement type. Supported types are:

- `behavioral` — externally observable runtime or tool behavior;
- `structural` — repository, interface, packaging, or architecture shape;
- `process` — required development, bootstrap, review, or operational workflow.

Requirement type describes what kind of obligation exists. It does **not** decide
how the requirement is evaluated. A structural or process requirement may still
have an automated test, while a behavioral requirement may require analysis.

IDs must be unique project-wide and stable when only surrounding prose changes.
Choose names that identify the behavioral area rather than a test or current
implementation function.

## Application notes

Use application notes for material that is important but should not create an
independent evidence obligation, including:

- examples and rationale;
- caller usage guidance;
- persistence/integration patterns owned outside the module;
- deliberate non-guarantees such as unspecified ordering;
- explanatory summaries and cross-references;
- implementation guidance that creates no additional externally observable
  requirement.

Do not invent artificial tests merely to make such material appear covered.

## Summaries and interface references

Broad pipeline descriptions and interface summaries should reference detailed
requirements rather than restating the same behavior under another ID.

A public interface inventory can be useful, but signatures are not a substitute
for behavioral requirements when behavior matters.

## Evaluation activities

Evaluation activities live under:

```text
docs/contracts/evaluation/
```

Each current contract should have a corresponding evaluation document when its
requirements drive implementation or verification.

An evaluation activity:

1. references one or more requirement IDs;
2. identifies an assessment method;
3. describes sufficient setup/action/evidence to establish the requirements;
4. does not add, reinterpret, or weaken required behavior.

Supported methods:

- `automated-test` — observable behavior can be exercised reliably;
- `inspection` — a public structural property or absence of an interface is
  established by inspection;
- `analysis` — a conclusion requires reasoning across several observations.

Prefer automated tests when they can directly establish the obligation. If
`automated-test` is the correct method but its executable evidence is
intentionally deferred, declare the `Evidence:` value `planned` in the evaluation
activity. Do not substitute `analysis` merely to avoid a pre-implementation
traceability failure.

## Documentation navigation

Use ordinary repository-relative Markdown links. The documentation verification
group lints Markdown and validates repository-local link targets without network
access. When adding a contract or evaluation document, link it from the relevant
project documentation or index so humans and agents can navigate to it directly.

### Current contract documents

Add repository-relative Markdown links to current contract documents here.

- [Evaluation activities](evaluation/README.md)
- [Generated traceability](generated/README.md)

## Test traceability

Executable tests declare only requirements they actually establish:

```python
@covers("MOD-AREA-001")
def test_example():
    ...
```

The decorator is seeded at `tests/util/contract.py`.

Before attaching an ID, apply this counterfactual:

> If this exact requirement were violated while the other relevant behavior
> remained correct, would this test fail?

If the answer is no, the test must not claim the requirement.

Calling an API is not evidence by itself. A test must assert an observable
consequence sufficient for the evaluation activity.

One test may cover several requirements when the same scenario independently
establishes each one. One requirement may require several tests.

## Generated artifacts

Generate:

```text
python agent-framework/tools/contracts/generate_traceability.py
```

Check freshness and structural consistency:

```text
python agent-framework/tools/contracts/generate_traceability.py --check
```

Generated files:

```text
docs/contracts/generated/requirements.csv
docs/contracts/generated/traceability.csv
```

Do not edit them manually. The Markdown contracts remain authoritative.

The generated traceability matrix combines requirement type, evaluation
activities, and executable `@covers(...)` evidence. Its evaluation status uses
these meanings:

- `AUTOMATED` — all declared evaluation is automated and matching test evidence exists;
- `MIXED` — automated evidence exists and inspection or analysis is also required;
- `MANUAL-REVIEW` — the requirement is intentionally evaluated only by inspection
  and/or analysis;
- `PLANNED-AUTOMATED` — automated-test is the declared method, executable
  evidence is explicitly deferred with the `Evidence:` value `planned`, and no matching
  `@covers(...)` evidence exists yet;
- `MISSING-EVALUATION` — no evaluation activity is defined;
- `MISSING-AUTOMATED-EVIDENCE` — an `automated-test` activity exists but no test
  claims the requirement.

`MANUAL-REVIEW` is not a failure and does not mean the requirement is unmet. It
means the generator cannot decide satisfaction automatically; a reviewer must
perform the referenced evaluation activity. `PLANNED-AUTOMATED` is also a valid
pre-implementation state, but it must be resolved to real executable evidence
when the milestone responsible for that behavior is implemented.

## Review

Contract review has separate questions:

1. Is each requirement precise and independently assessable?
2. Does its evaluation activity describe sufficient evidence?
3. Does each `@covers(...)` declaration actually establish the claimed
   requirement?
4. Are any requirements missing evidence?
5. Are caller guidance, summaries, or non-guarantees incorrectly represented as
   executable requirements?

When required behavior changes, update in this order:

```text
contract
  -> evaluation activity
  -> tests / traceability claims
  -> implementation
  -> generated traceability artifacts
```
