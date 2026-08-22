# Verification

The framework owns the standard verification toolchain and verifies itself with
that same toolchain.

Docker-only complete verification:

```text
docker run --rm --mount type=bind,source=<framework-root>,target=/workspace --workdir /workspace agent-agent-framework-development python tools/run_verification.py
```

When host Python is intentionally available, the convenience dispatcher is:

```text
python tools/run_verification.py --container
```

Configured categories execute in their `agent-framework.toml` order. The
framework currently provides `code`, `tests`, `documentation`, `repository`,
`contracts`, `configuration`, `shell`, and `ci`.

Tool discovery and management are documented in
[Framework tools](../../tools/README.md).

## Documentation verification

The `documentation` category validates project-owned Markdown directly.
`markdownlint-cli2` checks Markdown structure and style, while `lychee --offline` verifies
repository-local links and anchors without contacting external websites.
Documentation navigation is expressed with ordinary repository-relative
Markdown links; no generated documentation site or Sphinx/MyST metadata is
required.

## Repository pre-commit verification

The framework repository includes `.githooks/pre-commit`. Enable it once per
checkout with:

```text
git config core.hooksPath .githooks
```

The hook is framework-repository-only. It builds the framework base and
development images using Docker cache where possible, then runs the complete
`tools/run_verification.py` gate inside the controlled development image. A
failing build or verification gate rejects the commit. The hook is not copied
by project bootstrap.

On Windows, Git executes shell hooks through Git for Windows/MSYS. The hook
disables MSYS path conversion for Docker arguments so container paths such as
`/workspace` are passed to Docker unchanged. The bind-mount source still uses
the native Windows checkout path.
