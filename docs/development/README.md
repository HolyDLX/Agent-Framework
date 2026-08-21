# Framework development

The framework is Python-oriented and verifies itself with the same standard
runner set supplied to consuming projects.

Complete verification when developing this repository standalone is executed in
the controlled Docker environment. When host Python is available, the convenience
dispatcher is:

```text
python tools/run_verification.py --container
```

Each framework checkout should also enable the repository-only pre-commit gate:

```text
git config core.hooksPath .githooks
```

The committed hook invokes Docker directly and runs complete verification before
every framework commit. It is intentionally absent from consumer templates.

The framework base image is defined by `container/Dockerfile`. The root
`Dockerfile` exists so the framework can dogfood the same base-image +
project-image model used by consuming repositories.

## Development documentation

- [Container model](container.md)
- [Verification](verification.md)
