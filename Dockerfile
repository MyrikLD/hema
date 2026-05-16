# Stage 1: Build frontend
FROM node:22-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime base
FROM python:3.12-slim AS runtime-base
ENV LC_CTYPE=C.utf8
ENV PATH="/venv/bin:$PATH"
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 3: Build Python env
FROM runtime-base AS builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --locked --no-install-project --python python3.12 --python-preference only-system
COPY src src
COPY README.md .
RUN uv sync --no-dev --locked --no-editable --python python3.12 --python-preference only-system

# Stage 4: Runtime
FROM runtime-base AS api
ARG UID=10001
RUN useradd \
    --create-home \
    --home-dir "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    app

ENV ROOT=/app

COPY --from=builder /venv /venv
COPY static/ /app/static/
COPY --from=frontend-builder /frontend/dist/ /app/frontend/dist/
COPY migrations/ /app/migrations/
COPY alembic.ini /app/alembic.ini
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

USER app
WORKDIR /app
EXPOSE 8000
STOPSIGNAL SIGINT

ENTRYPOINT ["/docker-entrypoint.sh"]
