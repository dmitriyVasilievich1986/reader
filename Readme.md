[![build-backend](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/build_backend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/build_backend.yml)
[![build-frontend](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/build_frontend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/build_frontend.yml)
[![test-backend](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/test_backend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/reader/actions/workflows/test_backend.yml)

# Reader

A self-hosted personal book library — browse, read, and watch your collection from any device.

---

## About

Reader is a two-tier application for managing a private book library and reading its contents page-by-page in the browser. The `backend/` service owns the data model (Authors, Books, Categories, Pages, Users), authentication, the SQL schema and migrations, and a paginated, filterable REST API. The `frontend/` is a React single-page app that consumes that API to render a book grid, a book detail view, and a paginated reader, signing requests with a JWT obtained from the login endpoint.

Users are provisioned through a CLI (no public sign-up); admin accounts can mutate the catalogue while regular accounts can browse and watch books. The frontend's production bundle is emitted directly into `backend/static/`, so the FastAPI service can serve the SPA from the same origin as the API in single-process deployments.

Per-tier setup, configuration, and API examples live in [`backend/Readme.md`](backend/Readme.md) and [`frontend/Readme.md`](frontend/Readme.md).

---

## Technology stack

### Backend (`backend/`)

| Layer         | Choice                                                           |
| ------------- | ---------------------------------------------------------------- |
| Language      | Python 3.13                                                      |
| Web framework | FastAPI                                                          |
| ASGI server   | Uvicorn                                                          |
| ORM           | SQLAlchemy 2.x (async) + Alembic for migrations                  |
| Drivers       | `aiosqlite` (SQLite), `psycopg[binary]` / `asyncpg` (PostgreSQL) |
| Auth          | PyJWT (HS256/384/512) + bcrypt password hashing                  |
| Validation    | Pydantic v2 + `pydantic-settings[yaml]`                          |
| CLI           | `asyncclick`                                                     |
| Logging       | Loguru                                                           |
| Tests         | Pytest, `pytest-asyncio`, `httpx` (ASGI transport)               |
| Tooling       | `uv` for dependency management, `ruff`, `mypy`                   |

### Frontend (`frontend/`)

| Layer            | Choice                                                  |
| ---------------- | ------------------------------------------------------- |
| Language         | TypeScript 5.6                                          |
| UI framework     | React 18                                                |
| Build / dev      | Vite 6                                                  |
| Routing          | `react-router` v7                                       |
| Component kit    | MUI (`@mui/material`, `@mui/icons-material`) + Emotion  |
| Styling          | Tailwind CSS 3 (Preflight disabled to coexist with MUI) |
| State management | Zustand (with Redux DevTools middleware)                |
| HTTP client      | Axios + `js-cookie` for bearer-token storage            |
| Utilities        | `dayjs`, `classnames`, `rison`                          |
| Tooling          | ESLint 9 (typescript-eslint, import order), Prettier    |
