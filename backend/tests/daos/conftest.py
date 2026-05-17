"""DAO test fixtures: migrate the per-test SQLite DB and open an AsyncSession."""

from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.database import AsyncDatabaseClient

from ..conftest import ALEMBIC_INI


@pytest.fixture
def migrated_db(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file,
    db_client: AsyncDatabaseClient,
) -> None:
    """Run ``alembic upgrade head`` against the per-test SQLite database.

    Depends on ``db_client`` so the AsyncDatabaseClient singleton is already
    created before alembic's ``env.py`` looks it up.
    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    cfg = Config(str(ALEMBIC_INI))
    command.upgrade(cfg, "head")


@pytest.fixture
async def session(
    migrated_db: None,
    db_client: AsyncDatabaseClient,
) -> AsyncIterator[AsyncSession]:
    """Yield an AsyncSession bound to the migrated SQLite database."""
    async with db_client.session_factory() as s:
        yield s
