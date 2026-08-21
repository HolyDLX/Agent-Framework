# Contract evaluation activities

This directory defines how independently assessable contract requirements are
expected to be demonstrated.

The contract remains the authoritative source of required behavior. Evaluation
activities do not create new behavior and must not reinterpret a contract.
They describe suitable evidence for deciding whether a requirement is
satisfied.

## Evaluation document navigation

Use ordinary Markdown links between a contract and its corresponding evaluation
document, or list the evaluation document from the contract index.
Repository-local link verification checks these targets without contacting
external websites.

### Current evaluation documents

Add repository-relative Markdown links to current evaluation documents here.

## Machine-readable activity syntax

Each activity starts with a stable level-two `EA-*` heading followed by
`Requirements:` and `Method:` metadata. Values must be backtick-delimited:

```markdown
## EA-MOD-AREA-001

Requirements: `MOD-AREA-001`
Method: `automated-test`

Exercise the public behavior and assert the required result.
```

An activity may reference multiple requirements or methods:

```markdown
Requirements: `MOD-AREA-001`, `MOD-AREA-002`
Method: `automated-test`, `inspection`
```

When `automated-test` is the correct evaluation method but executable evidence
is intentionally deferred to a later implementation milestone, add the optional
metadata line:

```markdown
Evidence: `planned`
```

The `Evidence:` value `planned` is valid only for activities whose methods
include `automated-test`. It explicitly permits the automated evidence to be
absent for now. Omitting `Evidence:` means automated evidence is expected now.
Once matching `@covers(...)` evidence exists, the generated status becomes
`AUTOMATED` or `MIXED` regardless of the earlier planning marker.

## Evaluation methods

An evaluation activity uses one or more of these methods:

- `automated-test` — executable behavior can be demonstrated through public
  interfaces;
- `inspection` — a structural/public-interface property is established by
  inspecting source, signatures, exported symbols, or absence of an API;
- `analysis` — the requirement is established by reasoning over several
  executable observations where no single direct test is sufficient.

Prefer `automated-test` whenever the externally observable obligation can be
reliably exercised.

Requirement type and evaluation method are deliberately independent. For
example, a `structural` requirement may be checked by an automated repository
test, while a `behavioral` requirement may need `analysis` when no single direct
test is sufficient.

Every requirement must be referenced by at least one evaluation activity. If an
activity declares `automated-test`, at least one executable `@covers(...)`
declaration must provide matching evidence unless every automated-test activity
for that requirement explicitly declares the `Evidence:` value `planned`.
Inspection- and analysis-only requirements are reported as `MANUAL-REVIEW`, not
as uncovered or failed. Explicitly deferred automated evidence is reported as
`PLANNED-AUTOMATED`.

## Relationship to `@covers(...)`

`@covers(...)` declares that an executable test contributes evidence for a
requirement. It is not itself proof that the requirement is adequately tested.

Before adding a requirement ID to a test, apply this counterfactual:

> If this requirement were violated while other relevant behavior remained
> correct, would this test fail?

If the answer is no, the test must not claim that requirement.

A requirement may need multiple tests or a parameterized test to satisfy its
evaluation activity. One test may cover multiple requirements when the same
scenario independently demonstrates each of them.

Application notes and deliberate non-guarantees do not receive requirement IDs
and therefore do not participate in executable traceability.
