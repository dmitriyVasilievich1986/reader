"""Tests for ``reader.services.database.async_client.AsyncDatabaseClient``."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from reader.config import AppConfig
from reader.services.database import AsyncDatabaseClient


class TestInit:
    """Construction-time behaviour of AsyncDatabaseClient."""

    def test_raises_when_app_config_missing(self) -> None:
        """No ``app_config`` is a programmer error and must fail loudly."""
        with pytest.raises(RuntimeError, match="App config is required"):
            AsyncDatabaseClient(app_config=None)

    def test_builds_engine_and_session_factory(self, db_client: AsyncDatabaseClient) -> None:
        """Engine and session factory are wired up on construction."""
        assert db_client.engine is not None
        assert isinstance(db_client.session_factory, async_sessionmaker)

    def test_engine_uses_configured_url(
        self,
        db_client: AsyncDatabaseClient,
        sqlite_db_path: Path,
    ) -> None:
        """The engine targets the database URL from app config, not a default."""
        assert db_client.engine.url.drivername == "sqlite+aiosqlite"
        assert db_client.engine.url.database == str(sqlite_db_path)

    def test_singleton_returns_same_instance(self, app_config: AppConfig) -> None:
        """Repeated construction yields the same shared instance."""
        first = AsyncDatabaseClient(app_config=app_config)
        second = AsyncDatabaseClient(app_config=app_config)
        assert first is second


class TestSqlitePragma:
    """Verify that foreign-key enforcement is enabled on SQLite connections."""

    async def test_foreign_keys_enabled_on_connection(
        self,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """The connect listener should set ``PRAGMA foreign_keys=ON`` for new connections."""
        async with db_client.session_factory() as session:
            result = await session.execute(text("PRAGMA foreign_keys"))
            assert result.scalar() == 1


class TestSessionFactory:
    """Behaviour of the async session factory and ``get_session`` generator."""

    async def test_session_factory_creates_async_session(
        self,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Each call to the factory yields a usable AsyncSession."""
        async with db_client.session_factory() as session:
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    async def test_get_session_yields_async_session(
        self,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """``get_session`` is an async generator that yields a working session."""
        agen = db_client.get_session()
        session = await agen.__anext__()
        try:
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 2"))
            assert result.scalar() == 2
        finally:
            with pytest.raises(StopAsyncIteration):
                await agen.__anext__()


class TestHealthcheck:
    """Healthcheck reports True on success and False when the DB is unreachable."""

    async def test_healthcheck_succeeds(self, db_client: AsyncDatabaseClient) -> None:
        """A simple SELECT 1 returns True for a reachable SQLite file."""
        assert await db_client.healthcheck() is True

    async def test_healthcheck_returns_false_on_sqlalchemy_error(
        self,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Any SQLAlchemyError raised during the probe collapses to False."""
        failing_session = AsyncMock()
        failing_session.execute.side_effect = SQLAlchemyError("boom")
        failing_session.__aenter__.return_value = failing_session
        failing_session.__aexit__.return_value = None

        with patch.object(db_client, "_session_factory", return_value=failing_session):
            assert await db_client.healthcheck() is False


class TestClose:
    """``close`` disposes the underlying engine."""

    async def test_close_disposes_engine(self, db_client: AsyncDatabaseClient) -> None:
        """Engine.dispose is awaited so pool connections are released."""
        mock_engine = AsyncMock()
        db_client._engine = mock_engine  # noqa: SLF001
        await db_client.close()
        mock_engine.dispose.assert_awaited_once()
