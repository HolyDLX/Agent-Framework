# ${display_name}

## Initial intent

${intent}

## Development

This project uses Python ${python_version} and the Agent Framework development
workflow under `agent-framework/`.

After installing the project, run the minimal scaffold with:

```text
python -m ${package_name}.main
```

Run complete verification inside the project development image:

```text
docker run --rm --mount type=bind,source=<project-root>,target=/workspace --workdir /workspace ${image_name} python run_verification.py
```
