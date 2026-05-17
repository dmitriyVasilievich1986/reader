"""API-layer pytest fixtures: migrated SQLite plus an httpx ``AsyncClient``.

Reuses the parent suite's ``app_config`` / ``db_client`` / ``test_config_file``
fixtures, applies Alembic migrations, builds the FastAPI app via
:func:`reader.modules.app.get_app`, and exposes an ``httpx.AsyncClient`` bound
to ``ASGITransport`` so tests can call the real route stack in-process.
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
from reader.services.database import AsyncDatabaseClient

from ..conftest import ALEMBIC_INI


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
    """Open an ``httpx.AsyncClient`` that drives the app via ``ASGITransport``.

    Args:
        app (FastAPI): Application built by the ``app`` fixture.

    Yields:
        AsyncClient: Client whose requests resolve against in-process routes
            without binding to a network port.

    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
