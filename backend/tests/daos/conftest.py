"""DAO-layer pytest fixtures: migrate per-test SQLite and expose ``AsyncSession``.

Fixtures compose the parent suite's SQLite config/database clients with Alembic
``upgrade head``, then yield a session for DAO tests against a real migrated schema.

See also ``tests.conftest`` for ``test_config_file``, ``db_client``, and
``ALEMBIC_INI``.
"""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.database import AsyncDatabaseClient

from ..conftest import ALEMBIC_INI


@pytest.fixture
def migrated_db(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file: Path,
    db_client: AsyncDatabaseClient,
) -> None:
    """Apply all Alembic migrations to the ephemeral SQLite database.

    Depends on ``db_client`` first so ``AsyncDatabaseClient`` singleton state
    matches what ``env.py`` resolves when migrations run.

    Args:
        monkeypatch (pytest.MonkeyPatch): Sets ``CONFIG_FILE_PATH`` for Alembic.
        test_config_file (pathlib.Path): Same YAML path as parent ``AppConfig``
            fixtures.
        db_client (AsyncDatabaseClient): Materialises the singleton before Alembic
            invokes application config.

    Returns:
        None

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    cfg = Config(str(ALEMBIC_INI))
    command.upgrade(cfg, "head")


@pytest.fixture
async def session(
    migrated_db: None,
    db_client: AsyncDatabaseClient,
) -> AsyncIterator[AsyncSession]:
    """Expose an ``AsyncSession`` against the migrated test database.

    Args:
        migrated_db (None): Side-effect fixture that upgrades schema before session
            use.
        db_client (AsyncDatabaseClient): Provides ``session_factory``.

    Yields:
        AsyncSession: Context-managed session rolled back implicitly when leaving
            the async ``with`` block after the test.

    """
    async with db_client.session_factory() as s:
        yield s
