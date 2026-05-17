"""Alembic migration environment configuration.

This module configures the Alembic migration environment for the Access Management Service.
It sets up the database connection, loads application settings, initializes the
database client, and provides functions to run migrations in both online and
offline modes.

The module handles async database connections and integrates with the application's
settings and database client to ensure migrations run against the correct database
with the proper schema configuration.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from loguru import logger

from reader.config import AppConfig
from reader.services.database import AsyncDatabaseClient, models
from reader.services.database.models.base import mapper_registry

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app_config = AppConfig.get_or_create()
db_client = AsyncDatabaseClient(app_config=app_config)

logger.info("Alembic migrations started")
logger.info(f"Models: {models.__all__}")


def do_run_migrations(connection):
    """Run Alembic migrations with a synchronous database connection.

    This function is called from within an async context via `connection.run_sync()`
    to bridge the async/sync boundary. It configures Alembic's context with the
    provided synchronous connection and executes all pending migrations within
    a database transaction.

    Args:
        connection: A synchronous SQLAlchemy Connection object passed from
            the async connection's `run_sync()` method. This connection is used
            by Alembic to execute migration scripts against the database.

    Note:
        This function must be called from an async context using
        `await connection.run_sync(do_run_migrations)` where `connection` is
        an async connection object.

    """
    context.configure(
        connection=connection,
        target_metadata=mapper_registry.metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in 'online' mode with async database connection.

    This function handles running Alembic migrations when a database connection
    is available. It initializes the database client within the running event
    loop, establishes an async connection to the database, and executes
    migrations by bridging to synchronous Alembic operations.

    The function ensures proper initialization of the database connector with
    the current event loop reference, which is required for Google Cloud SQL
    connector compatibility. After migrations complete, it properly closes
    the database connection manager to clean up resources.

    Raises:
        RuntimeError: If the database engine has not been initialized or if
            there are issues connecting to the database.
        Exception: Any exception raised during migration execution will be
            propagated, and the database connection will be properly closed.

    Note:
        This function must be called from within an async context, typically
        via `asyncio.run()` or from an existing async event loop.

    """
    async with db_client.engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await db_client.close()


def run_migrations_online():
    """Run migrations in 'online' mode.

    This is the main entry point for Alembic migrations. It creates a new
    asyncio event loop and runs the async migration process. This function
    is called automatically when Alembic executes migrations.

    The function handles the entire migration lifecycle:
    - Initializes the database client
    - Establishes database connection
    - Executes pending migrations
    - Cleans up database connections

    Note:
        This function is called automatically by Alembic when running
        migrations. It should not be called directly in normal usage.

    """
    asyncio.run(run_async_migrations())


run_migrations_online()
