# Write or refine a contract

Use this skill when defining or restructuring externally observable module
behavior.

1. Read `docs/contracts/README.md` and `docs/contracts/evaluation/README.md`.
2. Establish terminology/model before writing detailed requirements.
3. Give an ID only to an independently assessable obligation and declare its
   type as `behavioral`, `structural`, or `process`.
4. Keep requirement type separate from evaluation method; do not classify a
   requirement by whether it happens to have a unit test.
5. Split clauses that can be violated independently. Do not strengthen an
   established product statement into additional observable guarantees merely
   to make it easier to test.
6. Move caller guidance, rationale, examples, and deliberate non-guarantees to
   application notes instead of inventing coverage obligations.
7. Avoid duplicate summary requirements; cross-reference detailed elements.
8. Create/update evaluation activities using `automated-test`, `inspection`, or
   `analysis` and state sufficient evidence without adding behavior. When an
   automated test is the correct method but the implementation/evidence is
   intentionally deferred, keep a `Method:` line containing `automated-test` and
   add the `Evidence:` value `planned` rather than substituting a manual method.
9. Only after contract + evaluation review, create/update tests and
   `@covers(...)` declarations for automated-test evidence.
10. Keep Markdown navigation current: link each contract from
    `docs/contracts/README.md` and each evaluation document from
    `docs/contracts/evaluation/README.md` using repository-relative Markdown
    links.
11. Regenerate traceability and review `PLANNED-AUTOMATED`, `MANUAL-REVIEW`,
    missing evaluation, missing automated evidence, and broad coverage claims.
