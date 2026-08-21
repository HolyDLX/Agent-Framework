# Verify change

Use this skill repeatedly during implementation to get fast, relevant feedback
without replacing the complete verification gate required before milestone
completion.

## Objective

Run the smallest verification that can meaningfully exercise the behavior or
files just changed, diagnose failures at the correct layer, and widen the
verification scope as an implementation slice stabilizes.

This skill is a development feedback loop. It does **not** replace the complete
verification procedure in `agent-framework/workflow/04-verification.md`.

## Preconditions

1. Read the consuming project's root `AGENTS.md`.
2. Read `agent-framework/workflow/04-verification.md`.
3. Read the current milestone and the authoritative specifications relevant to
   the change.
4. Use the framework development container. If the image has not already been
   checked for the current milestone, run:

   ```text
   python agent-framework/tools/container/docker_helper.py --build-if-missing
   ```

   Do not substitute host-only verification for required container checks.

   When host Python is unavailable, invoke the same runner directly inside the
   existing project development image as described by
   `agent-framework/workflow/04-verification.md`; host Python is optional.

## Choose the narrowest useful check

Select verification by what changed, not by habit.

| Change | Start with |
| --- | --- |
| One function or small implementation branch | directly relevant unit test or test selection |
| One module's behavior | that module's unit/contract tests |
| Public behavior governed by a contract | relevant contract tests plus contract traceability |
| Cross-module behavior | relevant integration tests |
| Formatting, lint, typing, or docstrings | `code` verification group or the failing diagnostic runner |
| Documentation only | `docs` verification group |
| Contract/evaluation/coverage metadata | `contracts` verification group |
| Repository scripts/configuration | `repository` verification group |
| Completed implementation slice touching several concerns | all relevant focused groups |
| Milestone completion or handover | complete verification |

Do not run the entire suite after every tiny edit when a focused test gives the
same immediate signal. Do not stay with focused tests once the changed behavior
crosses their boundary.

## Focused test examples

Run a specific test file:

```text
python agent-framework/tools/run_pytest.py --container tests/unit/test_example.py -q
```

Run a selected test or expression:

```text
python agent-framework/tools/run_pytest.py --container tests/unit/test_example.py -k name -q
```

Run the relevant aggregate verification group when the implementation slice is
broader:

```text
python agent-framework/tools/run_verification.py --container code
python agent-framework/tools/run_verification.py --container testing
python agent-framework/tools/run_verification.py --container docs
python agent-framework/tools/run_verification.py --container contracts
python agent-framework/tools/run_verification.py --container repository
```

Use an individual framework runner when diagnosing one gate, for example:

```text
python agent-framework/tools/run_ruff.py --container
python agent-framework/tools/run_pyright.py --container
python agent-framework/tools/run_pytest.py --container <selection>
```

## Contract-aware verification

When externally observable behavior is governed by a contract:

1. Read the exact requirement elements and corresponding evaluation activities.
2. Run the tests that are intended to provide evidence for the changed
   requirements.
3. If requirement IDs, evaluation mappings, or `@covers(...)` declarations
   changed intentionally, regenerate the inventories:

   ```text
   python agent-framework/tools/contracts/generate_traceability.py
   ```

4. Check contract verification:

   ```text
   python agent-framework/tools/run_verification.py --container contracts
   ```

5. Do not treat an `AUTOMATED` or `MIXED` traceability row as proof of semantic adequacy. For
   each claimed requirement, apply the counterfactual:

   > If this exact requirement were violated while the other relevant behavior
   > remained correct, would this test fail?

If the answer is no, the evidence or mapping is inadequate even if structural
traceability passes.

## Failure handling

When a focused check fails, determine which layer is wrong before editing:

- implementation defect;
- test defect;
- contract or evaluation-specification defect;
- framework/tooling defect;
- environment/container defect.

Do not weaken tests, verification settings, coverage thresholds, or contracts
merely to make a check pass.

If the AI sanitizer reports advisory milestone-reference `REVIEW` lines, inspect
each occurrence. Confirmed direct references to specific milestones belong
under `docs/planning/`; remove or relocate them elsewhere. Treat false positives
as reviewed warnings rather than suppressing the entire check.

If a legitimate project need cannot be expressed through the current framework,
improve `agent-framework` so the capability is explicit and reusable rather
than creating an untracked project-local verification fork.

After fixing a failure, rerun the smallest check that demonstrated the failure.
Then widen verification enough to exercise the surrounding behavior affected by
the fix.

## Escalation during implementation

Use this progression as the normal development loop:

```text
edit
  -> focused test/check
  -> fix and rerun focused check
  -> relevant verification group(s)
  -> continue implementation
```

When an implementation slice is complete, run every focused group relevant to
that slice before moving on when practical.

Before milestone completion or handover, always run the canonical complete gate:

```text
python agent-framework/tools/run_verification.py --container
```

Passing focused verification never replaces this final combined result.

## Reporting

When verification is material to a progress update or handover, state:

- what was run;
- what passed or failed;
- what failure class was identified when applicable;
- what broader verification remains before completion.

Do not claim a check was run unless it was actually executed.
