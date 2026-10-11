FROM node:24-slim AS frontend

WORKDIR /opt/frontend
ARG VITE_API_HOST=
ARG VITE_IMAGES_HOST=/static/images

COPY ./frontend /opt/frontend

RUN mkdir -p /opt/backend/static
RUN npm ci
RUN npm run build

FROM python:3.13-slim-bookworm AS build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

WORKDIR /opt/backend

# Install dependencies from pyproject.toml
COPY ./backend/pyproject.toml ./
COPY ./backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project --link-mode=copy --no-editable

FROM python:3.13-slim-bookworm AS production

WORKDIR /opt/backend

COPY --from=build /opt/backend/.venv /opt/backend/.venv
COPY ./backend/pyproject.toml ./
COPY ./backend/src ./src
COPY --from=frontend /opt/backend/static /opt/backend/static
COPY ./backend/configurations ./configurations

# Add binaries for run inside container
ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

EXPOSE 8000

ENTRYPOINT ["python", "src/reader"]
