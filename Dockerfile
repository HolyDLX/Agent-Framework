ARG AGENT_FRAMEWORK_BASE_IMAGE=agent-framework-python:3.12-local
FROM ${AGENT_FRAMEWORK_BASE_IMAGE}
WORKDIR /workspace
COPY . /workspace
CMD ["python", "tools/run_verification.py"]
