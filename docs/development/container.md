# Development container

The framework uses two image layers when verifying itself.

1. `container/Dockerfile` provides Python and every dependency required by the
   standard verification runners.
2. The root `Dockerfile` builds on that image for framework self-verification.

The canonical workspace inside the container is `/workspace`.

Docker-only build path:

```text
docker build --build-arg PYTHON_VERSION=3.12 --tag agent-framework-python:3.12-local --file container/Dockerfile container
docker build --tag agent-agent-framework-development --build-arg AGENT_FRAMEWORK_BASE_IMAGE=agent-framework-python:3.12-local .
```

When host Python is intentionally available, the convenience helper is:

```text
python tools/container/docker_helper.py --build-if-missing
```
