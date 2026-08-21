# Project-specific development guidance

The standard Python engineering toolchain, container execution policy, and
verification runners are owned by `agent-framework/`.

Use this directory only for development facts specific to this project, such as
runtime services, fixtures, generated resources, external emulators, or other
setup that the generic framework cannot define.

Docker is the canonical controlled execution environment. Host Python is an
optional convenience, not a bootstrap prerequisite.

## Development documentation

- [Container usage](container.md)
- [Verification](verification.md)
