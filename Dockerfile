# Same runtime as the inline Dockerfile in docker-compose-TrueNAS.yml.
# This file installs the local checkout. The TrueNAS file downloads the
# public GitHub zip instead, because that machine has no checkout.

FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_CACHE=1

ARG MCP_PROXY_VERSION=0.12.0
RUN uv venv /app/venv_mcp-proxy
# mcp-proxy 0.12.0 uses the mcp 1.x handler API
RUN uv pip install --python /app/venv_mcp-proxy/bin/python "mcp-proxy==${MCP_PROXY_VERSION}" "mcp<2"
RUN /app/venv_mcp-proxy/bin/mcp-proxy --version

WORKDIR /tmp/src
COPY pyproject.toml README.md ./
COPY src/ ./src/
ARG SOURCE_COMMIT=local
RUN printf '%s\n' "${SOURCE_COMMIT}" > /app/SOURCE_COMMIT
RUN uv venv /app/venv_strictdoc-mcp
RUN uv pip install --python /app/venv_strictdoc-mcp/bin/python .
RUN /app/venv_strictdoc-mcp/bin/python -c "import strictdoc_mcp.server"

FROM python:3.11-slim

ARG APP_UID=568
ARG APP_GID=568
RUN groupadd --gid "${APP_GID}" appuser
RUN useradd --uid "${APP_UID}" --gid "${APP_GID}" --create-home appuser
COPY --from=builder /app /app
ENV PATH="/app/venv_strictdoc-mcp/bin:/app/venv_mcp-proxy/bin:${PATH}"
RUN mkdir -p /data
RUN chown appuser:appuser /data
WORKDIR /data
VOLUME ["/data"]
USER appuser
EXPOSE 20423
ENTRYPOINT ["mcp-proxy", "--host", "0.0.0.0", "--port", "20423", "--pass-environment", "--", "strictdoc-mcp"]
