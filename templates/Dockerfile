ARG AGENT_FRAMEWORK_BASE_IMAGE=agent-framework-python:${python_version}-local
FROM $${AGENT_FRAMEWORK_BASE_IMAGE}

WORKDIR /workspace

# The framework base image already provides the standard development and
# verification toolchain. The project image adds only the consuming project's
# package/runtime dependencies.
COPY . /workspace
RUN python -m pip install --editable .

CMD ["python", "run_verification.py"]
