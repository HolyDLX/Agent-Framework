# Verification

The framework owns the standard verification toolchain. Project-specific
development documentation must not redefine those gates.

## Docker-only host

Run complete verification inside the already-built project development image:

```text
docker run --rm --mount type=bind,source=<project-root>,target=/workspace --workdir /workspace <project-development-image> python agent-framework/tools/run_verification.py
```

The bootstrap process should replace/document the actual project image name and
host-appropriate mount spelling for the consuming repository.

Focused groups append one of these arguments to the command:

```text
code
docs
testing
contracts
repository
```

## Documentation verification

The `docs` group validates project-owned Markdown directly. `markdownlint-cli2`
checks Markdown structure and style, while `lychee --offline` verifies
repository-local links and anchors without contacting external websites.
Documentation navigation is expressed with ordinary repository-relative
Markdown links; no generated documentation site or Sphinx/MyST metadata is
required.

## Optional host-Python convenience

When host Python is intentionally available, the equivalent framework
dispatcher is:

```text
python agent-framework/tools/run_verification.py --container
```

When a project legitimately needs a variation that the framework cannot
express, improve the framework/configuration model rather than copying a runner
into the project.
