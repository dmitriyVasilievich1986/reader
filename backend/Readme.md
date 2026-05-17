# Reader Backend

Async FastAPI service that exposes a paginated, filterable CRUD API for a
personal book library. The backend owns the data model (Authors, Books, Pages,
Categories), the database schema and migrations, and the HTTP surface consumed
by the frontend.

---

## Technology stack

| Layer            | Choice                                              |
| ---------------- | --------------------------------------------------- |
| Language         | Python 3.13                                         |
| Web framework    | FastAPI                                             |
| ASGI server      | Uvicorn                                             |
| ORM              | SQLAlchemy 2.x (async) + Alembic for migrations     |
| Drivers          | `aiosqlite` (SQLite), `psycopg[binary]` / `asyncpg` (PostgreSQL) |
| Validation       | Pydantic v2 + `pydantic-settings[yaml]`             |
| CLI              | `asyncclick`                                        |
| Logging          | Loguru                                              |
| Tests            | Pytest, `pytest-asyncio`, `httpx` (ASGI transport)  |
| Tooling          | `uv` for dependency management, `ruff`, `mypy`      |

---

## Project layout

```
backend/
├── configurations/          # YAML configs per environment (local, prod)
├── src/reader/
│   ├── config/              # AppConfig + nested Pydantic settings models
│   ├── modules/
│   │   ├── app.py           # FastAPI factory (get_app)
│   │   ├── middlewares/
│   │   │   ├── app_lifespan.py
│   │   │   └── dependencies/    # get_config, get_db
│   │   └── routers/
│   │       ├── api/
│   │       │   ├── system/      # /api/health, /api/version
│   │       │   └── v1/          # /api/v1/{author,book,category,page}
│   │       └── models/          # request, response, query, pagination models
│   ├── services/
│   │   ├── alembic/         # Migration env + versions/
│   │   ├── daos/            # AuthorDAO, BookDAO, CategoryDAO, PageDAO
│   │   └── database/        # AsyncDatabaseClient + ORM models
│   └── utils/               # Filter DSL, Singleton, CLI, static mounts
├── tests/
│   ├── api/                 # httpx-driven endpoint tests
│   ├── daos/                # DAO-layer tests against migrated SQLite
│   ├── test_async_client.py
│   ├── test_filter.py
│   └── test_migrations.py
└── pyproject.toml
```

---

## Major services

### `AppConfig` (`reader.config`)
Pydantic-settings model loaded from a YAML file referenced by the
`CONFIG_FILE_PATH` environment variable. Composes `Info` (API/CORS/paths) and
`Services` (database) sub-models. Implemented as a singleton via
`AppConfig.get_or_create()`, with a `reload=True` escape hatch used by tests.

### `AsyncDatabaseClient` (`reader.services.database`)
Singleton owning a single async SQLAlchemy engine and `async_sessionmaker`.
Builds the connection URL from `AppConfig`, enables `PRAGMA foreign_keys=ON`
for SQLite, exposes `session_factory`, an async-generator `get_session` for
FastAPI DI, plus `healthcheck()` and `close()`.

### `BaseDAO[Model]` (`reader.services.daos.base`)
Generic async DAO over a single SQLAlchemy declarative model. Provides
`get_by_pk`, `get_all` (pagination + filters + sorting + eager loads),
`create`, `update`, `delete`. Subclasses customise eager-load options via
`select_in_options_single` / `select_in_options_all` and projection via
`get_all_columns`. Concrete DAOs: `AuthorDAO`, `BookDAO`, `CategoryDAO`,
`PageDAO`.

### Routers (`reader.modules.routers`)
- `/api/health` — returns `503` when `AsyncDatabaseClient.healthcheck()` fails, else `200`.
- `/api/version` — returns the package version from `reader.__version__`.
- `/api/v1/author`, `/api/v1/book`, `/api/v1/category`, `/api/v1/page` — full CRUD per entity (`GET` list, `GET` by id, `POST`, `PATCH`, `DELETE`). All map `NoResultFound → 404`, `IntegrityError → 400`, and other `SQLAlchemyError → 500`.

### `Filter` DSL (`reader.utils.filter`)
Pydantic model representing a single WHERE clause (`field`, `op`, `value`).
Supports `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `like`, `ilike`, `isnull`,
`notnull`, with ISO-date coercion for comparison operators. Lists of `Filter`
are accepted on list endpoints via the `filters` query parameter (JSON-encoded
string).

### FastAPI factory (`reader.modules.app.get_app`)
Builds the app from `AppConfig`: title, version, debug, CORS middleware,
optional static mounts (`/assets`, `/images` when the directories exist), the
lifespan handler that initialises and disposes `AsyncDatabaseClient`, and
mounts the combined API router under `/api`.

### CLI (`reader.utils.cli.main`)
`asyncclick` group exposing `show-config` (prints resolved `AppConfig` as
JSON) and `run` (launches Uvicorn pointing at the FastAPI factory).
Registered as the `reader` console script in `pyproject.toml`.

---

## Configuration

Configuration is loaded from a YAML file. Point `CONFIG_FILE_PATH` at one of
the files in `configurations/`, or your own copy.

`configurations/local.yaml`:

```yaml
info:
    name: "Reader"
    description: "The application for reading books"
    api_info:
        app_port: 8000
        debug: true
        log_level: DEBUG
    cors_info:
        origins: "*"
        allow_credentials: true
        allow_methods: [GET, POST, PUT, DELETE]
        allow_headers: ["*"]

services:
    database:
        provider: "sqlite+aiosqlite"
        host: reader.sqlite3
```

For PostgreSQL, set `provider: "postgresql+psycopg"` (or `+asyncpg`) and add
`host`, `port`, `name`, `user`, `password`.

---

## Getting started

Prerequisites: Python 3.13 and [`uv`](https://github.com/astral-sh/uv).

```bash
# from backend/
uv sync                                              # install all deps + dev group
export CONFIG_FILE_PATH=$PWD/configurations/local.yaml
uv run alembic -c src/reader/services/alembic/alembic.ini upgrade head
uv run reader run --reload                           # http://localhost:8000
```

Inspect resolved configuration:

```bash
uv run reader show-config
```

API docs are exposed by FastAPI at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc:      `http://localhost:8000/redoc`

---

## API usage examples

All v1 endpoints serialise responses with `camelCase` keys (`firstName`,
`lastName`, `authorId`, `bookId`). Request bodies accept either snake_case or
camelCase.

### Create an author and a book

```bash
curl -X POST http://localhost:8000/api/v1/author \
  -H 'Content-Type: application/json' \
  -d '{"first_name": "Frank", "last_name": "Herbert"}'
# → 201 { "id": 1, "firstName": "Frank", "lastName": "Herbert", "cover": null }

curl -X POST http://localhost:8000/api/v1/book \
  -H 'Content-Type: application/json' \
  -d '{"name": "Dune", "author_id": 1}'
# → 201 { "id": 1, "name": "Dune", "authorId": 1, ... }
```

### List with pagination

```bash
curl 'http://localhost:8000/api/v1/book?limit=20&offset=0&sort_by=name&sort_order=asc'
```

Response shape:

```json
{
  "data": [ { "id": 1, "name": "Dune" } ],
  "metadata": {
    "total": 1,
    "offset": 0,
    "limit": 20,
    "sortBy": "name",
    "sortOrder": "asc",
    "filters": null
  }
}
```

### List with filters

`filters` accepts a JSON-encoded array. Each entry is `{field, op, value}`.

```bash
curl --get 'http://localhost:8000/api/v1/book' \
  --data-urlencode 'filters=[{"field":"name","op":"ilike","value":"dune"}]'
```

### Partial update

```bash
curl -X PATCH http://localhost:8000/api/v1/book/1 \
  -H 'Content-Type: application/json' \
  -d '{"description": "Arrakis epic"}'
```

### Delete

```bash
curl -X DELETE http://localhost:8000/api/v1/book/1   # → 204 No Content
```

### Health and version

```bash
curl http://localhost:8000/api/health    # 200 {"status":"ok"} or 503
curl http://localhost:8000/api/version   # {"version":"0.1.x"}
```

---

## Database migrations

Migrations live in `src/reader/services/alembic/migrations/versions/` and are
driven by the configuration's database URL.

```bash
# apply all
uv run alembic -c src/reader/services/alembic/alembic.ini upgrade head

# generate a new revision from model changes
uv run alembic -c src/reader/services/alembic/alembic.ini revision --autogenerate -m "describe change"

# revert
uv run alembic -c src/reader/services/alembic/alembic.ini downgrade -1
```

---

## Testing

The suite is split into DAO-layer tests against a migrated ephemeral SQLite
file, API-layer tests that drive the FastAPI app via `httpx.AsyncClient` over
`ASGITransport`, and unit tests for the filter DSL and migrations.

```bash
uv run pytest                       # full suite, with coverage
uv run pytest tests/api             # API integration tests only
uv run pytest -m "not slow"         # skip slow-marked tests
uv run pytest --no-cov -q           # quick run, no coverage
```

Markers (`pyproject.toml`): `asyncio`, `slow`, `integration`, `api`.
