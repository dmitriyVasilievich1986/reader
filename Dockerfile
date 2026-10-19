FROM node:24-slim AS frontend

WORKDIR /opt/frontend
ARG VITE_API_HOST=
ARG VITE_IMAGES_HOST=/static/images

COPY ./frontend /opt/frontend

RUN npm ci
RUN npm run build

FROM python:3.13-slim-bookworm AS build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

WORKDIR /opt/backend

# Install dependencies and the project (provides the `reader` CLI)
COPY ./backend/pyproject.toml ./
COPY ./backend/uv.lock ./
COPY ./backend/Readme.md ./
COPY ./backend/LICENSE ./
COPY ./backend/src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --group sqlite --link-mode=copy --no-editable

FROM python:3.13-slim-bookworm AS production

ENV ENVIRONMENT=prod

# Run as an unprivileged user instead of root
RUN groupadd --system reader \
    && useradd --system --gid reader --no-create-home --home-dir /opt/backend reader

WORKDIR /opt/backend

COPY --from=build /opt/backend/.venv /opt/backend/.venv
COPY ./backend/pyproject.toml ./
COPY ./backend/src ./src
COPY --from=frontend --chown=reader:reader /opt/frontend/dist /opt/backend/static
COPY ./backend/configurations ./configurations

# The app writes book images into static/ and may create files in its workdir
RUN chown reader:reader /opt/backend

# Add binaries for run inside container
ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

USER reader

EXPOSE 8000

ENTRYPOINT ["python", "src/reader"]
