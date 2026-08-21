# Implement milestone

Use this skill for implementation of the milestone marked `Current` in the
consuming project's `docs/planning/roadmap.md`.

1. Read the project root `AGENTS.md` and all framework workflow documents.
2. Read `docs/planning/README.md`, the roadmap, current milestone, and relevant
   authoritative architecture/contracts/evaluation/development docs.
3. Inspect relevant source/tests and `git status`.
4. Implement only the bounded milestone scope, following
   `workflow/03-implementation.md` and `workflow/06-module-development-workflow.md`.
5. Update contracts before tests/implementation when required behavior changes.
6. Keep evaluation activities aligned with assessable contract requirements.
   When the milestone implements behavior whose automated evidence was marked
   the `Evidence:` value `planned`, create the required tests and `@covers(...)` evidence;
   do not hand over the responsible milestone while that requirement remains
   `PLANNED-AUTOMATED`.
7. Use `agent-framework/skills/verify-change/SKILL.md` repeatedly during
   implementation for focused feedback, and complete container verification
   before handover.
8. Regenerate/check traceability where applicable.
9. Create/update the milestone handover and roadmap state according to the
   planning workflow.
