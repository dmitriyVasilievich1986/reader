"""API-layer pytest fixtures: migrated SQLite plus an httpx ``AsyncClient``.

Reuses the parent suite's ``app_config`` / ``db_client`` / ``test_config_file``
fixtures, applies Alembic migrations, builds the FastAPI app via
:func:`reader.modules.app.get_app`, and exposes ``httpx.AsyncClient`` fixtures
bound to ``ASGITransport`` so tests can call the real route stack in-process.

Three client flavors are exposed:

* ``client`` — anonymous; for negative auth-path tests.
* ``admin_client`` — seeded admin user; default for CRUD tests that exercise
  ``admin_required`` endpoints.
* ``user_client`` — seeded non-admin user; for ``user_authorized`` reads and
  403 mutations.
"""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from reader.config import AppConfig
from reader.modules.app import get_app
from reader.services.daos import UserDAO
from reader.services.database import AsyncDatabaseClient

from ..conftest import ALEMBIC_INI

ADMIN_CREDENTIALS = {"username": "admin", "password": "adminpw"}
USER_CREDENTIALS = {"username": "user", "password": "userpw"}


@pytest.fixture
def migrated_db(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file: Path,
    db_client: AsyncDatabaseClient,
) -> None:
    """Apply all Alembic migrations to the ephemeral SQLite database.

    Mirrors the DAO-layer fixture so API tests share schema setup without
    coupling to the daos conftest.

    Args:
        monkeypatch (pytest.MonkeyPatch): Sets ``CONFIG_FILE_PATH`` for Alembic.
        test_config_file (pathlib.Path): YAML written by the parent fixture.
        db_client (AsyncDatabaseClient): Materialises the singleton before
            Alembic invokes application config.

    Returns:
        None

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    cfg = Config(str(ALEMBIC_INI))
    command.upgrade(cfg, "head")


@pytest.fixture
def app(app_config: AppConfig, migrated_db: None) -> FastAPI:
    """Build the FastAPI app against the per-test ``AppConfig``.

    Args:
        app_config (AppConfig): Reloaded configuration pointing at the test
            SQLite file.
        migrated_db (None): Ensures the schema exists before any request.

    Returns:
        FastAPI: Configured application instance.

    """
    return get_app(config=app_config)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Open an anonymous ``httpx.AsyncClient`` against the in-process app.

    Args:
        app (FastAPI): Application built by the ``app`` fixture.

    Yields:
        AsyncClient: Client whose requests resolve against in-process routes
            without binding to a network port.

    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def seed_admin_user(
    migrated_db: None,
    db_client: AsyncDatabaseClient,
) -> dict[str, str]:
    """Persist an admin user against the migrated database.

    Args:
        migrated_db (None): Ensures schema exists before insert.
        db_client (AsyncDatabaseClient): Database client bound to the test
            SQLite file.

    Returns:
        dict[str, str]: ``username`` / ``password`` pair usable with the
            ``/api/v1/user/login`` endpoint.

    """
    users = UserDAO(database_client=db_client)
    await users.create(
        username=ADMIN_CREDENTIALS["username"],
        email="admin@example.com",
        password=ADMIN_CREDENTIALS["password"],
        is_admin=True,
    )
    return ADMIN_CREDENTIALS


@pytest.fixture
async def seed_regular_user(
    migrated_db: None,
    db_client: AsyncDatabaseClient,
) -> dict[str, str]:
    """Persist a non-admin user against the migrated database.

    Args:
        migrated_db (None): Ensures schema exists before insert.
        db_client (AsyncDatabaseClient): Database client bound to the test
            SQLite file.

    Returns:
        dict[str, str]: ``username`` / ``password`` pair usable with the
            ``/api/v1/user/login`` endpoint.

    """
    users = UserDAO(database_client=db_client)
    await users.create(
        username=USER_CREDENTIALS["username"],
        email="user@example.com",
        password=USER_CREDENTIALS["password"],
        is_admin=False,
    )
    return USER_CREDENTIALS


async def _authenticated_client(app: FastAPI, credentials: dict[str, str]) -> AsyncIterator[AsyncClient]:
    """Yield an ``AsyncClient`` whose default headers carry a fresh JWT.

    Args:
        app (FastAPI): Application driven by ``ASGITransport``.
        credentials (dict[str, str]): Username / password posted to login.

    Yields:
        AsyncClient: Client with ``Authorization: Bearer <token>`` preset from
            a live call to ``/api/v1/user/login``.

    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/user/login", json=credentials)
        response.raise_for_status()
        ac.headers["Authorization"] = f"Bearer {response.json()['accessToken']}"
        yield ac


@pytest.fixture
async def admin_client(
    app: FastAPI,
    seed_admin_user: dict[str, str],
) -> AsyncIterator[AsyncClient]:
    """Yield an ``AsyncClient`` authenticated as the seeded admin user.

    Args:
        app (FastAPI): Application built by the ``app`` fixture.
        seed_admin_user (dict[str, str]): Admin credentials seeded into the
            database before the client logs in.

    Yields:
        AsyncClient: Client carrying a valid admin Bearer token by default.

    """
    async for ac in _authenticated_client(app, seed_admin_user):
        yield ac


@pytest.fixture
async def user_client(
    app: FastAPI,
    seed_regular_user: dict[str, str],
) -> AsyncIterator[AsyncClient]:
    """Yield an ``AsyncClient`` authenticated as a non-admin user.

    Args:
        app (FastAPI): Application built by the ``app`` fixture.
        seed_regular_user (dict[str, str]): Non-admin credentials seeded into
            the database before the client logs in.

    Yields:
        AsyncClient: Client carrying a valid non-admin Bearer token by default.

    """
    async for ac in _authenticated_client(app, seed_regular_user):
        yield ac
