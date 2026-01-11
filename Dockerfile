# syntax=docker/dockerfile:1.9

# Stage 1: Runtime base (minimal)
FROM debian:stable-slim AS runtime-base
# Assure UTF-8 encoding is used.
ENV LC_CTYPE=C.utf8
# Location of the virtual environment
ENV UV_PROJECT_ENVIRONMENT="/venv"
# Location of the python installation via uv
ENV UV_PYTHON_INSTALL_DIR="/python"
# Tweaking the PATH variable for easier use
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"
# Install only runtime dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y tzdata ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Build application
FROM runtime-base AS builder
# Byte compile the python files on installation
ENV UV_COMPILE_BYTECODE=1
# Python version to use
ENV UV_PYTHON=python3.12

# Install build dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential gettext git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies (cached layer)
RUN uv sync --no-dev --locked --no-install-project

# Copy application code and install project
COPY src src
COPY README.md .
RUN uv pip install --no-deps .

# Stage 3: Runtime
FROM runtime-base AS api
# Create non-privileged user
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN useradd \
    --create-home \
    --home-dir "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    app

STOPSIGNAL SIGINT

# Copy Python and virtual env from builder
COPY --from=builder $UV_PYTHON_INSTALL_DIR $UV_PYTHON_INSTALL_DIR
COPY --from=builder $UV_PROJECT_ENVIRONMENT $UV_PROJECT_ENVIRONMENT
COPY static/ /app/static

USER app
WORKDIR /app
EXPOSE 8000
