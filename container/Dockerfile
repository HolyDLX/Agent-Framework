ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    RUNNING_IN_CONTAINER=1

ARG ACTIONLINT_VERSION=1.7.12
ARG NODEJS_VERSION=22.23.2
ARG NODEJS_SHA256=d60acfe00a2932254bb0ad20e01b0d74397a0875595de719654b214f4b03f307
ARG MARKDOWNLINT_CLI2_VERSION=0.23.2
ARG LYCHEE_VERSION=0.24.2
ARG LYCHEE_SHA256=73657a111819a30c47c08352896796f23d64e4eb2b3ed39b6d32149241566fc5

# /workspace belongs to the consuming project at runtime.
WORKDIR /workspace

COPY requirements.txt /opt/agent-framework/requirements.txt

RUN python -m pip install --upgrade pip \
    && apt-get update \
    && apt-get install --no-install-recommends --yes \
       ca-certificates \
       curl \
       findutils \
       git \
       libatomic1 \
       shellcheck \
       xz-utils \
       yamllint \
    && curl --fail --silent --show-error --location \
      "https://nodejs.org/download/release/v${NODEJS_VERSION}/node-v${NODEJS_VERSION}-linux-x64.tar.xz" \
      --output /tmp/node.tar.xz \
    && echo "${NODEJS_SHA256}  /tmp/node.tar.xz" | sha256sum --check - \
    && tar --extract --xz --file /tmp/node.tar.xz --directory /usr/local --strip-components=1 \
    && rm -f /tmp/node.tar.xz \
    && npm install --global "markdownlint-cli2@${MARKDOWNLINT_CLI2_VERSION}" \
    && curl --fail --silent --show-error --location \
      "https://github.com/lycheeverse/lychee/releases/download/lychee-v${LYCHEE_VERSION}/lychee-x86_64-unknown-linux-musl.tar.gz" \
      --output /tmp/lychee.tar.gz \
    && echo "${LYCHEE_SHA256}  /tmp/lychee.tar.gz" | sha256sum --check - \
    && mkdir -p /tmp/lychee \
    && tar --extract --gzip --file /tmp/lychee.tar.gz --directory /tmp/lychee \
    && LYCHEE_BIN="$(find /tmp/lychee -type f -name lychee -print -quit)" \
    && test -n "${LYCHEE_BIN}" \
    && install -m 0755 "${LYCHEE_BIN}" /usr/local/bin/lychee \
    && rm -rf /tmp/lychee /tmp/lychee.tar.gz \
    && curl --fail --silent --show-error --location \
      "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz" \
      --output /tmp/actionlint.tar.gz \
    && echo "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8  /tmp/actionlint.tar.gz" | sha256sum --check - \
    && tar --extract --gzip --file /tmp/actionlint.tar.gz --directory /usr/local/bin actionlint \
    && chmod 755 /usr/local/bin/actionlint \
    && rm -f /tmp/actionlint.tar.gz \
    && python -m pip install --requirement /opt/agent-framework/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Verify that every installed development tool with a supported version
# command is available in the resulting image.
RUN python --version \
    && python -m pip --version \
    && node --version \
    && npm --version \
    && curl --version \
    && git --version \
    && shellcheck --version \
    && yamllint --version \
    && actionlint -version \
    && markdownlint-cli2 --version \
    && lychee --version \
    && black --version \
    && ruff --version \
    && pyright --version \
    && pytest --version \
    && coverage --version \
    && pre-commit --version

CMD ["python", "--version"]
