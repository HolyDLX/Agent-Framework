# Development container

The project uses two image layers.

1. `agent-framework/container/Dockerfile` provides Python ${python_version} and
   every dependency required by the standard framework verification runners.
2. The project root `Dockerfile` builds from that framework image and installs
   only project package/runtime dependencies.

The canonical workspace inside the container is `/workspace`. Normal agent
verification bind-mounts the current checkout there so source edits do not
require an image rebuild.

Build the layers directly:

```text
docker build --build-arg PYTHON_VERSION=${python_version} --tag agent-framework-python:${python_version}-local --file agent-framework/container/Dockerfile agent-framework/container
docker build --tag ${image_name} --build-arg AGENT_FRAMEWORK_BASE_IMAGE=agent-framework-python:${python_version}-local .
```

On Linux, run writable bind mounts with the host identity and a writable home:

```text
docker run --rm --user "$$(id -u):$$(id -g)" --env HOME=/tmp --mount type=bind,source="$$PWD",target=/workspace --workdir /workspace ${image_name} python run_verification.py
```

When host Python is intentionally available, this convenience helper performs
the same image checks/builds:

```text
python agent-framework/tools/container/docker_helper.py --build-if-missing
```

Use `--rebuild` after framework/base-image or project dependency changes.
