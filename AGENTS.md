# AGENTS.md — Reader

Project-level guidance for AI coding agents. Each tier has its own detailed
rules — read them before changing code there:

- [`backend/AGENTS.md`](backend/AGENTS.md) — FastAPI service, DB, migrations, tests
- [`frontend/AGENTS.md`](frontend/AGENTS.md) — React SPA (Vite+), Oxlint/Oxfmt rules

## What the project is

Reader is a self-hosted personal book library: users browse a catalogue of
authors, books, categories and pages and read books page by page in the
browser. Users are created only through the backend CLI; admins can change the
catalogue, regular users can read and "watch" books.

## Repository layout

```
reader/
├── backend/                  # Python 3.13 FastAPI API (uv) — see backend/AGENTS.md
├── frontend/                 # React + TypeScript SPA (Vite) — see frontend/AGENTS.md
├── nginx/
│   ├── config/nginx.conf     # Full stack: static SPA + /api proxy to backend
│   ├── config/nginx-infra.conf  # Infra-only: static files, /api → 404
│   └── ssl/                  # TLS cert/key (git-ignored)
├── db/data/                  # Postgres volume (git-ignored)
├── Dockerfile                # Multi-stage image: frontend build → backend venv → runtime
├── docker-compose.yaml       # Main deployment: nginx + postgres + backend
├── docker-compose-infra.yaml # nginx + postgres only (backend run outside Docker)
└── .github/workflows/        # CI: build_backend, build_frontend, test_backend
```

## How frontend and backend work together

The frontend has no server of its own — it is a static bundle that talks
**only** to the backend's REST API. Treat them as one product:

- **Build output.** `npm run build` writes the bundle to `frontend/dist/`
  (`index.html` + `assets/`); the Docker image copies it into
  `/opt/backend/static`. The backend serves it via the
  `/assets` and `/images` static mounts and a catch-all route that returns
  `index.html` for client-side routing. In Docker, nginx serves the same files.
- **API contract.** The frontend calls `/api/v1/...` through one Axios client
  (`frontend/src/services/apiClient/`). Backend responses use camelCase keys;
  list endpoints return `{ data, metadata }` and accept
  `limit`, `offset`, `sortBy`, `sortOrder` and a JSON-encoded `filters` param
  that maps onto the backend `Filter` DSL.
- **Auth.** `POST /api/v1/user/login` returns a JWT; the frontend keeps it in
  the `accessToken` cookie and sends `Authorization: Bearer <token>`. A 401
  redirects to `/login`. Reads need a user, mutations need an admin.
- **Origin.** `VITE_API_HOST` sets the API origin. Leave it empty when the
  frontend and API share an origin (Docker/nginx); set it to
  `http://localhost:8000` for the Vite dev server (backend CORS allows it).
- **Changing the contract.** When you change a backend route, request/response
  model or field name, update the matching TypeScript types and client in
  `frontend/src/services/apiClient/<resource>/` in the same branch, and the
  other way around. Don't leave the two out of sync.

## Deployment: Docker Compose

**`docker-compose.yaml` is the main way to deploy the project.** Don't add
other deployment paths without discussing it first.

```bash
docker build -t reader:latest .   # builds frontend + backend into one image
docker compose up -d              # nginx + db + backend
docker compose logs -f backend
docker compose down
```

- `Dockerfile` stages: `frontend` (Node 24, `npm ci && npm run build`) →
  `build` (uv sync of backend deps, no dev group) → `production`
  (Python 3.13 slim, runs `python src/reader`, port 8000).
- Services in `docker-compose.yaml`:
  - `nginx` — ports 80/443, serves the SPA from the shared `reader-static`
    volume, images from `backend/static/images`, proxies `/api/` to
    `backend:8000`. Needs `nginx/ssl/reader.pem` and `reader.key`.
  - `db` — Postgres 18, env from `backend/db.env`, data in `db/data/`.
  - `backend` — image `reader:latest`, env from `backend/.env` (+ optional
    `backend/db.env`), `CONFIG_FILE_PATH=/opt/backend/configurations/local.yaml`.
    `backend/configurations` and `backend/src` are mounted in.
- `docker-compose-infra.yaml` runs only nginx + Postgres (DB on 5432) so the
  backend can be run on the host (`uv run --env-file=.env reader run`).
- Run DB migrations against the deployed DB with Alembic from the backend
  (see `backend/AGENTS.md`).
- Never commit `backend/.env`, `backend/db.env`, `nginx/ssl/` or `db/data/`.

If you change ports, paths, env vars or the build output location, update
`Dockerfile`, both compose files and `nginx/config/*.conf` together.

## CI

GitHub Actions run on pushes and PRs to `main` and `development`:

- `build_backend.yml` — `ruff check`, `ruff format --check`, `ty check`, `uv build`
- `test_backend.yml` — `pytest`
- `build_frontend.yml` — `voidzero-dev/setup-vp` (`vp install`), `vp check`, `vp run build`

Run the same checks locally before opening a PR (commands are in the tier
AGENTS files).

### Pre-commit

`.pre-commit-config.yaml` runs the linters (ruff, ty, oxlint, oxfmt),
basic file hygiene checks, and blocks commits to `main`/`development`.
`pre-commit` is in the backend dev group:

```bash
cd backend
uv run pre-commit install            # once per clone
uv run pre-commit run --all-files    # run every hook manually
```

## Git workflow

### Protected branches

- `main` and `development` are **protected**. **Never commit or push directly
  to them.** All changes go through a pull request.
- If you are on `main` or `development`, create a new branch before making any
  commit.

### Branch names

Every new branch must use one of these prefixes:

- `FEATURE/<short-description>` — new functionality, refactors, docs, chores
- `BUGFIX/<short-description>` — bug fixes

Use kebab-case after the prefix, e.g. `FEATURE/Add-AGENTS-files`,
`BUGFIX/fix-books-pagination`.

### Commit messages

A short title in [Conventional Commits](https://www.conventionalcommits.org/)
style: `<type>: <summary>`.

Allowed types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`,
`perf`, `ci`, `build`.

- Title: imperative mood, about 72 characters or less, no trailing period
  (`feat: Add slug field to books`, `fix: Update backend cors config`).
- Body: **only when the title isn't enough**. Leave a blank line after the title,
  then a short bulleted list of changes:

```
feat: Add book watch counter

- Add watches_count column and Alembic revision
- Add POST /api/v1/book/{book_id}/watch endpoint
- Increment counter when a book page is opened in the frontend
```

- Keep one logical change per commit; don't mix backend and frontend changes
  that are unrelated.
