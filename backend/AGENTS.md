# AGENTS.md — Backend

Guidance for AI coding agents working inside `backend/`. This file covers the
backend only; project-level architecture (frontend, Docker, nginx, CI) is
described elsewhere.

## Stack

- Python 3.13, managed with [`uv`](https://github.com/astral-sh/uv) (`pyproject.toml` + `uv.lock`)
- FastAPI + Uvicorn
- SQLAlchemy 2.x **async** ORM, Alembic migrations
- Drivers: `aiosqlite` (local/tests), `psycopg` / `asyncpg` (PostgreSQL)
- Pydantic v2 + `pydantic-settings[yaml]` for config
- `asyncclick` CLI, Loguru logging, `bcrypt` + `pyjwt` for auth
- Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`, `ty`

## Running commands

**Every command goes through `uv run` with the `.env` file**, from `backend/`:

```bash
uv run --env-file=.env <command>
```

`.env` provides `CONFIG_FILE_PATH` (the YAML config to load) and the
`SERVICES__AUTH__*` secrets. Without it, config falls back to
`configurations/prod.yaml` and auth secrets are missing. Never call `python`,
`pytest`, `ruff`, `ty`, `alembic` or `reader` directly, and never `pip install`.

```bash
uv sync                                               # install deps (incl. dev group)
uv add <pkg> / uv add --dev <pkg>                     # add a dependency (updates uv.lock)

uv run --env-file=.env pytest                         # all tests + coverage
uv run --env-file=.env pytest tests/api/test_books_api.py -k slug
uv run --env-file=.env ruff check src tests           # lint
uv run --env-file=.env ruff check src tests --fix     # lint with autofix
uv run --env-file=.env ruff format src tests          # format
uv run --env-file=.env ty check                       # type-check (src/reader)

uv run --env-file=.env reader run                     # start the API (http://localhost:8000)
uv run --env-file=.env reader show-config             # print resolved AppConfig
uv run --env-file=.env reader add-book --book-path <dir> [--preview]
uv run --env-file=.env reader user create-user --username ... --email ... [--is-admin] --password

uv run --env-file=.env alembic -c src/reader/services/alembic/alembic.ini upgrade head
uv run --env-file=.env alembic -c src/reader/services/alembic/alembic.ini revision --autogenerate -m "<message>"
```

Before finishing a change, all of these must pass:

```bash
uv run --env-file=.env ruff check src tests
uv run --env-file=.env ruff format --check src tests
uv run --env-file=.env ty check
uv run --env-file=.env pytest
```

`notebooks/` is scratch space and is not lint-clean; don't lint it or fix it as
part of unrelated work.

## Source layout

```
src/reader/
├── __init__.py            # __version__ (hatch reads the package version here)
├── __main__.py            # python -m reader → uvicorn
├── commands/              # Business workflows used by the CLI (base.py, add_book/)
├── config/                # AppConfig (singleton, YAML + env) and nested settings models
├── modules/
│   ├── app.py             # get_app() FastAPI factory
│   ├── middlewares/       # lifespan + dependencies (get_config, get_db, user_authorized, admin_required)
│   └── routers/
│       ├── api/system/    # /api/health, /api/version
│       ├── api/v1/        # /api/v1/{author,book,category,page,user}
│       ├── index.py       # SPA index route
│       └── models/        # base/, requests/<entity>/, responses/<entity>/
├── services/
│   ├── alembic/           # alembic.ini + migrations/ (env.py, versions/)
│   ├── auth/              # PasswordService, JWTTokenService
│   ├── daos/              # BaseDAO + one DAO per model
│   └── database/          # AsyncDatabaseClient + ORM models
└── utils/                 # Filter DSL, Singleton, CLI, static mounts
tests/
├── conftest.py            # singleton reset, temp SQLite, test YAML, AppConfig, db_client
├── api/                   # httpx ASGITransport endpoint tests (client / admin_client / user_client)
├── auth/                  # password + JWT services
├── daos/                  # DAO tests against a migrated SQLite DB
└── migrations/            # one test module per Alembic revision + full pipeline
```

## Conventions

### Modules and exports

- One public class/function per file, file named in snake_case after it
  (`get_all_books_query.py` → `GetAllBooksQuery`).
- Every module declares `__all__` right after its docstring.
- Packages re-export their public names in `__init__.py` (with `__all__`);
  import from the package, e.g. `from reader.services.daos import UserDAO`.
- Use absolute `reader.` imports across packages; relative imports
  (`from .base import BaseDAO`) only within the same package.

### Routers (`modules/routers/api/v1/<entity>.py`)

- `router = APIRouter(prefix="/<entity>", tags=["<Entities>"])`, registered in
  `api/v1/__init__.py`.
- Parameters use `Annotated[...]` with `Path`, `Query`, `Body`, `Depends`.
  The DB comes from `db: Annotated[AsyncDatabaseClient, Depends(get_db)]`.
- Auth goes in the decorator: `dependencies=[Depends(user_authorized)]` for reads,
  `dependencies=[Depends(admin_required)]` for mutations.
- Set `response_model`, `status_code` and `summary` on each route.
- Handlers build a DAO, call it inside `try`, and map errors to `HTTPException`
  (always `raise ... from e`, log with Loguru):
  - `NoResultFound` → 404
  - `IntegrityError` → 400
  - other `SQLAlchemyError` → 500
- Return `<Response>.model_validate(orm_obj)`; list endpoints return
  `{ data, metadata: PaginationMetadata }`.

### Request / response models (`modules/routers/models/`)

- Requests inherit `BaseRequestModel` (accept camelCase and snake_case).
  Query models for lists build on `PaginationWithFiltersQuery`.
- Responses inherit `BaseResponseModel` / `BaseResponseFromModelSchema`
  (`from_attributes`, serialized as camelCase).
- Naming: `Post<Entity>Body`, `Patch<Entity>Body`, `GetAll<Entities>Query`,
  `GetSingle<Entity>Response`, `GetAll<Entities>Response`, `Simple<Entity>Response`.
- Every field uses `Field(..., description=...)` plus validation limits.
- PATCH handlers pass `body.model_dump(exclude_unset=True)`.

### Data access (`services/daos/`)

- All DB access goes through a DAO subclassing `BaseDAO[Model]`. Routers never
  build queries or touch sessions directly.
- Configure via class attributes: `database_model`, `get_all_columns`,
  `select_in_options_single`, `select_in_options_all`, `base_filters`.
- A DAO accepts either `database_client` (opens a session per call) or a shared
  `session`. New methods follow the existing pair pattern: a private
  `_<name>_raw(session, ...)` that does the work, and a public `<name>(...)`
  that picks the session.
- List filtering uses the `Filter` DSL (`reader.utils.models.filter`);
  don't hand-parse filter strings.

### ORM models and migrations (`services/database/models/`, `services/alembic/`)

- Models inherit `Base` (and `DateTimeMixin` for `created_at`/`updated_at`),
  use `Mapped[...]` + `mapped_column(...)`, and put relationship type imports
  under `if TYPE_CHECKING:`.
- Any schema change needs a new Alembic revision in
  `services/alembic/migrations/versions/` (file name template
  `YYYY-MM-DD_HH-MM_<rev>_<slug>.py`) with working `upgrade()` **and** `downgrade()`,
  plus a test module `tests/migrations/test_<slug>_revision.py` covering both
  directions. Never edit an existing revision.

### Config

- `AppConfig.get_or_create()` returns the singleton; inject it in routes via
  `get_config`. Don't read env vars directly elsewhere.
- Values come from the YAML at `CONFIG_FILE_PATH`, overridden by env vars with
  the `__` nested delimiter (`SERVICES__AUTH__JWT_SECRET_KEY`).
- New settings go into a Pydantic model under `config/models/` and the YAML files
  in `configurations/`. Never commit real secrets.

### Logging and errors

- Use `from loguru import logger`; `print` is forbidden (ruff `T20`).
- Log with `logger.exception(...)` when re-raising unexpected errors.

### Tests

- Mirror the source tree under `tests/`; files `test_*.py`, functions `test_*`,
  classes `Test*`. `asyncio_mode = "auto"`, so async tests need no decorator.
- Use the shared fixtures (`app_config`, `db_client`, `migrated_db`, `client`,
  `admin_client`, `user_client`) instead of building apps or engines ad hoc.
  Tests run against a temporary SQLite file, never `reader.sqlite3`.
- Markers must be declared (`--strict-markers`): `asyncio`, `slow`,
  `integration`, `api`.
- Every new route, DAO method or migration gets tests, including error paths
  (401/403/404/400).

## Docstrings (required)

**Every module, class, function and method — including private helpers,
`__init__`, properties, fixtures and tests — must have a docstring.** Use
**Google style** with the **type of every argument** in parentheses. ruff's
`D` rules enforce presence and layout (`D203`/`D213` are ignored, so use
`D211`/`D212`: no blank line before a class docstring, summary on the first line).

Rules:

- Module docstring at the top of the file, before `__all__` and imports.
- First line: one-sentence imperative summary ending with a period.
- `Args:` lists every parameter as `name (type): Description.`; mark optional
  ones `(type, optional)` and state `Defaults to X.`. Include `*args (Any)` /
  `**kwargs (Any)`. Omit `self` / `cls`.
- `Returns:` as `type: Description.` (use `None` when nothing is returned);
  generators/fixtures that yield use `Yields:`.
- `Raises:` only for exceptions the body actually raises, as
  `ExceptionType: When it happens.`
- Classes document public attributes in `Attributes:` as `name (type): Description.`
- Leave a blank line before the closing `"""` of multi-section docstrings
  (existing style).

Example:

```python
"""DAO for the Book model."""

__all__ = ("BookDAO",)


class BookDAO(BaseDAO[Book]):
    """Data-access object for ``Book`` rows."""

    async def get_by_slug(self, slug: str, filters: list[dict[str, Any]] | None = None) -> Book:
        """Return the book whose ``slug`` matches.

        Args:
            slug (str): Slug value to resolve.
            filters (list[dict[str, Any]] | None, optional): Extra WHERE clauses.
                Defaults to None.

        Returns:
            Book: Matching ORM instance.

        Raises:
            NoResultFound: When no book has this slug.

        """
```

## Typing (ty)

Type-checked with Astral's [ty](https://docs.astral.sh/ty/) (`[tool.ty]` in
`pyproject.toml`, scope `src/reader`). Warnings fail the check.

- Ruff `ANN` rules: annotate every parameter and return type (including
  `-> None`); `Any` is allowed. Tests are exempt.
- `unsound-return-statement` is an error: don't return `Any` from a function
  with a concrete return type — narrow or `cast` it.
- Use modern syntax: `X | None`, `list[int]`, PEP 695 generics (`class BaseDAO[M: Base]`).
- Unused ignores are errors: only add `# ty: ignore[<rule>]` with a specific
  ty rule when needed. mypy-style `# type: ignore[code]` is not honoured.

## Ruff

Configured in `pyproject.toml`.

**Format** (`[tool.ruff.format]`): Black-compatible — double quotes, spaces,
magic trailing commas respected, line length **120**.

**Lint** (`[tool.ruff.lint]`), target `py313`, enabled rule sets:

| Code    | Plugin           | What it means here                                                   |
| ------- | ---------------- | -------------------------------------------------------------------- |
| `A`     | flake8-builtins  | Don't shadow builtins (`id`, `type`, `object`, ...)                  |
| `ARG`   | unused-arguments | Remove unused args or prefix with `_`; `# noqa: ARG001` for fixtures |
| `ASYNC` | flake8-async     | No blocking calls inside `async def`                                 |
| `PTH`   | use-pathlib      | Use `pathlib.Path`, not `os.path` / `open()`                         |
| `B`     | bugbear          | Common bugs (mutable defaults, `raise ... from`, ...)                |
| `E`/`W` | pycodestyle      | Style errors/warnings, max line 120                                  |
| `F`     | Pyflakes         | Unused imports/variables, undefined names                            |
| `N`     | pep8-naming      | snake_case functions, PascalCase classes                             |
| `RUF`   | Ruff-specific    | e.g. sorted `__all__`, mutable class defaults                        |
| `SLF`   | flake8-self      | No private member access across objects (`# noqa: SLF001` in tests)  |
| `RET`   | flake8-return    | No redundant `else` after `return`, consistent returns               |
| `Q`     | flake8-quotes    | Double quotes                                                        |
| `T20`   | flake8-print     | No `print`; use Loguru                                               |
| `COM`   | flake8-commas    | Trailing commas                                                      |
| `D`     | pydocstyle       | Docstrings required everywhere (see above)                           |
| `FIX`   | flake8-fixme     | No `TODO`/`FIXME`/`XXX` left in code                                 |
| `I`     | isort            | Import sorting                                                       |

Ignored: `E712` (`== True` allowed for SQLAlchemy), `RUF001`, `N814`, `N817`,
`RUF100`, `COM812`, `D203`, `D213`.

Unused variables are allowed when prefixed with `_`.

**Imports** (`[tool.ruff.lint.isort]`): sections future → stdlib → third-party
→ first-party (`reader`) → local folder (`.`), one blank line between them,
case-insensitive sorting, `combine-as-imports = true`. Run
`ruff check --fix` to sort automatically.

## Don'ts

- Don't run tools outside `uv run --env-file=.env`.
- Don't edit `static/` (frontend build output), `htmlcov/`, `.venv/` or the
  local `*.sqlite3` files.
- Don't commit `.env` secrets or real credentials in `configurations/*.yaml`.
- Don't add sync DB drivers or blocking I/O in request handlers.
- Don't bypass DAOs or add endpoints without auth dependencies.
