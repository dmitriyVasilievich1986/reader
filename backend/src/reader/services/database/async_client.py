"""Async SQLAlchemy engine and session management for the application."""

__all__ = ("AsyncDatabaseClient",)

from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import ConnectionPoolEntry

from reader.config import AppConfig
from reader.utils.singleton import Singleton


class AsyncDatabaseClient(metaclass=Singleton):
    """Singleton that owns the async engine and session factory."""

    _engine: AsyncEngine
    _session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, app_config: AppConfig | None = None) -> None:
        """Build the async engine and session factory from app configuration.

        For SQLite, registers a connect hook that enables ``PRAGMA foreign_keys``.

        Args:
            app_config (AppConfig | None, optional): Application config with
                database URL and options. Defaults to None.

        Returns:
            None

        Raises:
            RuntimeError: If ``app_config`` is None.

        """
        if app_config is None:
            raise RuntimeError("App config is required")
        logger.info(f"Initializing database client with URL: {app_config.services.database.url}")

        self._engine = create_async_engine(
            app_config.services.database.url,
            echo=app_config.info.api_info.debug,
            future=True,
        )
        if app_config.services.database.provider.startswith("sqlite"):
            event.listen(self._engine.sync_engine, "connect", self._set_sqlite_pragma)
        self._session_factory = async_sessionmaker[AsyncSession](
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Database client initialized successfully.")

    @staticmethod
    def _set_sqlite_pragma(dbapi_connection: object, _connection_record: ConnectionPoolEntry) -> None:
        """Enable foreign-key enforcement for a new SQLite connection.

        Args:
            dbapi_connection (object): DBAPI connection from the pool.
            _connection_record (ConnectionPoolEntry): Pool entry (unused).

        Returns:
            None

        """
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    @property
    def engine(self) -> AsyncEngine:
        """Return the shared async SQLAlchemy engine.

        Returns:
            AsyncEngine: The configured engine instance.

        """
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the factory used to create async sessions.

        Returns:
            async_sessionmaker[AsyncSession]: Session factory with
                ``expire_on_commit=False``.

        """
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a context-managed async session for request-scoped work.

        Yields:
            AsyncSession: A session that is closed when the async context exits.

        """
        async with self._session_factory() as session:
            yield session

    async def close(self) -> None:
        """Dispose of the engine and release pool connections.

        Returns:
            None

        """
        await self._engine.dispose()
        logger.info("Database client closed successfully.")

    async def healthcheck(self) -> bool:
        """Run a simple ``SELECT 1`` to verify the database is reachable.

        Returns:
            bool: True if the query succeeds, False on ``SQLAlchemyError``.

        """
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            return False

        return True
