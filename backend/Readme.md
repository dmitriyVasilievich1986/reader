# Reader Backend

Async FastAPI service that exposes a paginated, filterable CRUD API for a
personal book library. The backend owns the data model (Authors, Books, Pages,
Categories), the database schema and migrations, and the HTTP surface consumed
by the frontend.

---

## Technology stack

| Layer         | Choice                                                           |
| ------------- | ---------------------------------------------------------------- |
| Language      | Python 3.13                                                      |
| Web framework | FastAPI                                                          |
| ASGI server   | Uvicorn                                                          |
| ORM           | SQLAlchemy 2.x (async) + Alembic for migrations                  |
| Drivers       | `aiosqlite` (SQLite), `psycopg[binary]` / `asyncpg` (PostgreSQL) |
| Validation    | Pydantic v2 + `pydantic-settings[yaml]`                          |
| CLI           | `asyncclick`                                                     |
| Logging       | Loguru                                                           |
| Tests         | Pytest, `pytest-asyncio`, `httpx` (ASGI transport)               |
| Tooling       | `uv` for dependency management, `ruff`, `mypy`                   |

---

## Project layout

```
backend/
├── configurations/          # YAML configs per environment (local, prod)
├── src/reader/
│   ├── commands/            # CLI workflows (e.g. add_book)
│   ├── config/              # AppConfig + nested Pydantic settings models
│   ├── modules/
│   │   ├── app.py           # FastAPI factory (get_app)
│   │   ├── middlewares/
│   │   │   ├── app_lifespan.py
│   │   │   └── dependencies/    # get_config, get_db, user_authorized, admin_required
│   │   └── routers/
│   │       ├── api/
│   │       │   ├── system/      # /api/health, /api/version
│   │       │   └── v1/          # /api/v1/{author,book,category,page,user}
│   │       └── models/          # request, response, query, pagination models
│   ├── services/
│   │   ├── alembic/         # Migration env + versions/
│   │   ├── auth/            # PasswordService, JWTTokenService
│   │   ├── daos/            # AuthorDAO, BookDAO, CategoryDAO, PageDAO, UserDAO
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
`Services` (database, auth) sub-models. Implemented as a singleton via
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
`PageDAO`, `UserDAO`.

### Auth (`reader.services.auth`)

- `PasswordService` — bcrypt hashing and verification used by the user CLI
  and login route.
- `JWTTokenService` — issues and decodes HS256-signed JWTs containing
  `user_id` and `exp` (1 day lifetime by default). Secret and algorithm come
  from `AppConfig.services.auth`.
- Dependencies: `user_authorized` validates an `Authorization: Bearer <jwt>`
  header and resolves the row to a `User`; `admin_required` wraps it and
  additionally checks `user.is_admin`.

### Routers (`reader.modules.routers`)

- `/api/health` — returns `503` when `AsyncDatabaseClient.healthcheck()` fails, else `200`.
- `/api/version` — returns the package version from `reader.__version__`.
- `/api/v1/user/login` — exchanges username + password for a JWT.
- `/api/v1/user/me` — `GET` / `PATCH` the authenticated user's profile.
- `/api/v1/author`, `/api/v1/book`, `/api/v1/category`, `/api/v1/page` — full CRUD per entity (`GET` list, `GET` by id, `POST`, `PATCH`, `DELETE`). Reads require a valid user JWT; mutations require an admin JWT. All map `NoResultFound → 404`, `IntegrityError → 400`, missing/invalid token → `401`, non-admin caller on a mutation → `403`, and other `SQLAlchemyError → 500`.
- `/api/v1/book/{book_id}/watch` — `POST` increments a book's `watchesCount` and returns the updated row (auth required, admin not required).

### `Filter` DSL (`reader.utils.models.filter`)

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

`asyncclick` group registered as the `reader` console script in
`pyproject.toml`. Commands:

- `show-config` — prints the resolved `AppConfig` as JSON.
- `run` — launches Uvicorn pointing at the FastAPI factory.
- `add-book --book-path <dir> [--preview]` — ingest a book from a local
  directory, or print a dry-run plan.
- `user create-user --username --email --password [--is-admin] [--first-name] [--last-name] [--photo-url]` —
  provision a new account (the only way to create users).
- `user check-password --username --password` — verify a stored hash.

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
  auth:
    jwt_secret_key: "change-me-in-prod"
    jwt_algorithm: "HS256"   # HS256 | HS384 | HS512
```

For PostgreSQL, set `provider: "postgresql+psycopg"` (or `+asyncpg`) and add
`host`, `port`, `name`, `user`, `password`. `services.auth.jwt_secret_key`
is required and used to sign login tokens.

---

## Getting started

Prerequisites: Python 3.13 and [`uv`](https://github.com/astral-sh/uv).

```bash
# from backend/
uv sync                                              # install all deps + dev group
export CONFIG_FILE_PATH=$PWD/configurations/local.yaml
uv run alembic -c src/reader/services/alembic/alembic.ini upgrade head
uv run reader user create-user \                     # bootstrap an admin
  --username admin --email admin@example.com --is-admin --password
uv run reader run --reload                           # http://localhost:8000
```

Inspect resolved configuration:

```bash
uv run reader show-config
```

API docs are exposed by FastAPI at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API usage examples

All v1 endpoints serialise responses with `camelCase` keys (`firstName`,
`lastName`, `authorId`, `bookId`, `createdAt`, `watchesCount`). Request
bodies accept either snake_case or camelCase. Timestamps are ISO 8601 in
UTC. Entity rows include `createdAt` and `updatedAt`; user rows additionally
include `isActive`.

### Create a user (CLI) and log in

There is no public sign-up endpoint — users are provisioned through the
CLI. Use `--is-admin` for accounts that need to mutate authors, books,
categories, or pages.

```bash
uv run reader user create-user \
  --username alice --email alice@example.com --is-admin --password
# prompted for password, then prints the created user as JSON

curl -X POST http://localhost:8000/api/v1/user/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "s3cret"}'
# → 200
# {
#   "accessToken": "eyJhbGciOiJIUzI1NiIs...",
#   "expiresAt": "2026-05-20T12:34:56Z"
# }
```

Every endpoint below (except `/api/health`, `/api/version`, and
`/api/v1/user/login`) requires `Authorization: Bearer <accessToken>`.
Mutating endpoints additionally require an admin user; non-admin callers
get `403`.

### Current user

```bash
TOKEN=eyJhbGciOiJIUzI1NiIs...

curl http://localhost:8000/api/v1/user/me \
  -H "Authorization: Bearer $TOKEN"
# → 200
# {
#   "id": 1,
#   "username": "alice",
#   "email": "alice@example.com",
#   "firstName": null,
#   "lastName": null,
#   "photoUrl": null,
#   "isActive": true,
#   "createdAt": "2026-05-19T09:00:00Z",
#   "updatedAt": "2026-05-19T09:00:00Z"
# }

curl -X PATCH http://localhost:8000/api/v1/user/me \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"first_name": "Alice"}'
```

### Create an author and a book (admin)

```bash
curl -X POST http://localhost:8000/api/v1/author \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"first_name": "Frank", "last_name": "Herbert"}'
# → 201
# {
#   "id": 1,
#   "firstName": "Frank",
#   "lastName": "Herbert",
#   "cover": null,
#   "createdAt": "2026-05-19T09:01:00Z",
#   "updatedAt": "2026-05-19T09:01:00Z"
# }

curl -X POST http://localhost:8000/api/v1/book \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name": "Dune", "author_id": 1}'
# → 201
# {
#   "id": 1,
#   "name": "Dune",
#   "description": null,
#   "cover": null,
#   "authorId": 1,
#   "watchesCount": 0,
#   "author": {
#     "id": 1,
#     "firstName": "Frank",
#     "lastName": "Herbert",
#     "cover": null,
#     "createdAt": "2026-05-19T09:01:00Z",
#     "updatedAt": "2026-05-19T09:01:00Z"
#   },
#   "createdAt": "2026-05-19T09:02:00Z",
#   "updatedAt": "2026-05-19T09:02:00Z"
# }
```

### List with pagination

```bash
curl --get 'http://localhost:8000/api/v1/book' \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'limit=20' \
  --data-urlencode 'offset=0' \
  --data-urlencode 'sort_by=name' \
  --data-urlencode 'sort_order=asc'
```

Response shape — list items use the same model as the single-book endpoint,
including the embedded `author` object:

```json
{
  "data": [
    {
      "id": 1,
      "name": "Dune",
      "description": null,
      "cover": null,
      "authorId": 1,
      "watchesCount": 0,
      "author": {
        "id": 1,
        "firstName": "Frank",
        "lastName": "Herbert",
        "cover": null,
        "createdAt": "2026-05-19T09:01:00Z",
        "updatedAt": "2026-05-19T09:01:00Z"
      },
      "createdAt": "2026-05-19T09:02:00Z",
      "updatedAt": "2026-05-19T09:02:00Z"
    }
  ],
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

`sort_by` is constrained per entity (e.g. books accept `id`, `name`,
`author_id`, `created_at`, `updated_at`). `limit` is capped at 100.

### List with filters

`filters` accepts a JSON-encoded array. Each entry is `{field, op, value}`.

```bash
curl --get 'http://localhost:8000/api/v1/book' \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'filters=[{"field":"name","op":"ilike","value":"dune"}]'
```

### Watch a book

```bash
curl -X POST http://localhost:8000/api/v1/book/1/watch \
  -H "Authorization: Bearer $TOKEN"
# → 200 with the updated GetSingleBookResponse, watchesCount incremented
```

### Partial update (admin)

```bash
curl -X PATCH http://localhost:8000/api/v1/book/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"description": "Arrakis epic"}'
```

### Delete (admin)

```bash
curl -X DELETE http://localhost:8000/api/v1/book/1 \
  -H "Authorization: Bearer $TOKEN"
# → 204 No Content
```

### Pages

Pages mirror the book pattern. `GetSinglePageResponse` embeds the parent
`book` (as `SimpleBookResponse`, without nested author); list responses use
the lighter `SimplePageResponse` (no embedded book).

```bash
curl http://localhost:8000/api/v1/page/1 \
  -H "Authorization: Bearer $TOKEN"
# → 200
# {
#   "id": 1,
#   "position": 0,
#   "cover": "page-0.png",
#   "bookId": 1,
#   "book": {
#     "id": 1,
#     "name": "Dune",
#     "authorId": 1,
#     "description": null,
#     "cover": null,
#     "watchesCount": 0,
#     "createdAt": "2026-05-19T09:02:00Z",
#     "updatedAt": "2026-05-19T09:02:00Z"
#   },
#   "createdAt": "2026-05-19T09:03:00Z",
#   "updatedAt": "2026-05-19T09:03:00Z"
# }
```

### Health and version

```bash
curl http://localhost:8000/api/health    # 200 {"status":"ok"} or 503 {"detail":"..."}
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
