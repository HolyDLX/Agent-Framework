# Bootstrap project

Use this skill when a developer has created a clean Git repository, added this
repository as the `agent-framework/` submodule, and asks an agent to bootstrap a
new Python project.

## Objective

Create a deterministic, documented, and verifiable Python project scaffold.
Do not implement product features during bootstrap. Do not create product
contracts, evaluation activities, roadmap commitments, or an implementation
milestone.

## Preconditions

- `agent-framework/` is an initialized Git submodule at the expected recorded
  commit. Local changes inside it are permitted but must be reported.
- Docker Desktop or Docker Engine is available and running on an x86-64 host.
- The developer supplied an initial project intent.
- The consuming root contains only `.git`, `.gitmodules`, `agent-framework`, and
  entries matched by the framework's template `.gitignore`.

Adding and committing `.gitmodules` and the submodule gitlink before bootstrap
is recommended but not enforced.

## Procedure

1. Read `agent-framework/workflow/README.md` and all workflow documents.
2. Check `git status`. Do not remove or overwrite pre-existing work.
3. Derive a concise project display name from the repository root name or the
   supplied intent. The name may contain only ASCII letters, digits, spaces,
   underscores, and hyphens. It must normalize to a valid, non-keyword Python
   identifier.
4. Select Python 3.12 unless the developer requested Python 3.14. These are the
   framework's currently supported versions.
5. Build the framework base image from the consuming repository root, passing
   the selected version:

   ```text
   docker build --build-arg PYTHON_VERSION=<python-version> --tag agent-framework-python:<python-version>-local --file agent-framework/container/Dockerfile agent-framework/container
   ```

6. Run the canonical configuration command inside the framework image. Pass the
   developer's intent verbatim.

   PowerShell/Windows:

   ```powershell
   docker run --rm --mount "type=bind,source=$PWD,target=/workspace" --workdir /workspace agent-framework-python:<python-version>-local python agent-framework/configure.py --project-name "<project-name>" --intent "<initial-intent>" --python-version <python-version>
   ```

   Bash/Linux:

   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --env HOME=/tmp --mount type=bind,source="$PWD",target=/workspace --workdir /workspace agent-framework-python:<python-version>-local python agent-framework/configure.py --project-name "<project-name>" --intent "<initial-intent>" --python-version <python-version>
   ```

   The Linux identity mapping prevents root-owned files in the bind-mounted
   repository. Linux is supported but not the primary tested bootstrap host.
7. If configuration fails, report its complete preflight explanation. Do not
   delete conflicts or retry with destructive cleanup. Ignored IDE, virtual
   environment, cache, coverage, and build paths may be preserved with a
   warning.
8. Read the generated `AGENTS.md`, `README.md`, `docs/README.md`, architecture
   intent baseline, planning skeleton, contract/evaluation conventions,
   `pyproject.toml`, and `agent-framework.toml`.
9. Confirm the generated display name, distribution name, import package,
   Python version, and verbatim intent. Do not strengthen the intent into
   additional externally observable guarantees.
10. Treat the generated greeting and smoke test as replaceable scaffolding, not
    authoritative product behavior. The smoke test imports and calls `main()`
    only to prove the package is runnable and satisfy initial coverage.
11. Do not create product contracts or evaluation activities during bootstrap.
    The supplied intent is not sufficient authority for inventing behavioral
    guarantees.
12. Do not create an implementation milestone or populate the empty roadmap.
    Planning begins in a separate deliberate task.
13. Build the consuming project's development image:

    ```text
    docker build --tag <project-development-image> --build-arg AGENT_FRAMEWORK_BASE_IMAGE=agent-framework-python:<python-version>-local .
    ```

14. Run complete verification inside the project image.

    PowerShell/Windows:

    ```powershell
    docker run --rm --mount "type=bind,source=$PWD,target=/workspace" --workdir /workspace <project-development-image> python agent-framework/tools/run_verification.py --fix
    ```

    Bash/Linux:

    ```bash
    docker run --rm --user "$(id -u):$(id -g)" --env HOME=/tmp --mount type=bind,source="$PWD",target=/workspace --workdir /workspace <project-development-image> python agent-framework/tools/run_verification.py --fix
    ```

15. Fix only scaffold/framework integration defects required for verification.
    Do not implement product behavior.
16. Report the generated identity, warnings, verification status, and unresolved
    product decisions. Stop after bootstrap.
17. End with **bootstrap process feedback for the framework author**. State what
    worked and identify any friction, ambiguity, portability issue, scaffold
    defect, verification conflict, or missing capability. Distinguish project
    issues from framework/workflow issues.

## Ownership rules

- `agent-framework/`: reusable framework-owned process and tooling.
- Files created outside the submodule: project-owned seeds after configuration.
- `.agents/skills/`: thin discovery wrappers; canonical skill content remains
  under `agent-framework/skills/`.
- `tools/`: project-specific utilities only; do not copy standard framework
  runners into it.

Updating the framework submodule must not modify project-owned seed files.
Migration or reconfiguration of an existing project is outside the current
scope.

## Completion condition

Bootstrap is complete when deterministic configuration succeeds, the project
records its identity and initial intent, the minimal package can be imported and
run, the documentation/workflow structure exists, and complete verification
passes. Product specification and planning are later tasks.
