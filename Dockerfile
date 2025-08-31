FROM oven/bun:1 AS frontend

WORKDIR /app

RUN --mount=type=bind,target=/app/package.json,src=./frontend/package.json \
    --mount=type=bind,target=/app/bun.lock,src=./frontend/bun.lock \
    --mount=type=bind,target=/app/vite.config.ts,src=./frontend/vite.config.ts \
    --mount=type=bind,target=/app/tsconfig.json,src=./frontend/tsconfig.json \
    --mount=type=bind,target=/app/tsconfig.node.json,src=./frontend/tsconfig.node.json \
    --mount=type=bind,target=/app/tsconfig.app.json,src=./frontend/tsconfig.app.json \
    --mount=type=bind,target=/app/src,src=./frontend/src \
    bun install --frozen-lockfile --development && bunx tsc -b && bunx vite build --outDir=/app/dist --mode=production

FROM python:3.12-slim AS backend

WORKDIR /app

RUN mkdir -p /app/static/js

ENV APP_PORT=3000

COPY --from=frontend /app/dist /app/static/js
COPY ./reader /app/reader
COPY ./LICENSE /app/LICENSE
COPY ./Readme.md /app/Readme.md
COPY ./pyproject.toml /app/pyproject.toml


RUN --mount=type=bind,target=/app/uv.lock,src=./uv.lock \
    pip install uv && uv sync

EXPOSE ${APP_PORT}

CMD [ "sh", "-c", "uv run reader run --host 0.0.0.0 --port ${APP_PORT}" ]
