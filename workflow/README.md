# Agent workflow

These documents define the reusable development workflow for consuming Python
projects and for the framework itself.

Read all six before substantial project work:

1. [Scope and onboarding](01-scope-and-onboarding.md)
2. [Planning and milestones](02-planning-and-milestones.md)
3. [Implementation](03-implementation.md)
4. [Verification](04-verification.md)
5. [Review and handover](05-review-and-handover.md)
6. [Module development workflow](06-module-development-workflow.md)

## Path convention

The workflow is written from the perspective of a consuming repository:

- project-owned documentation is under `docs/`;
- reusable tooling is under `agent-framework/tools/`;
- reusable skills are under `agent-framework/skills/`.

When developing the framework repository itself, the same files are at the
repository root, so omit the `agent-framework/` prefix when invoking tools.

The framework defines **process**. Project-specific documentation defines
**project truth**. If a project exposes a legitimate need not supported by the
framework, prefer extending the framework with a deliberate configuration
point instead of patching its toolchain ad hoc in the project.
