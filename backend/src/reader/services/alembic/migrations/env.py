"""Alembic environment configuration for async SQLAlchemy migrations.

Wires Alembic to application settings and ``mapper_registry.metadata``,
then runs online migrations when this module is executed by the Alembic CLI.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from loguru import logger
from sqlalchemy.engine import Connection

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


def do_run_migrations(connection: Connection) -> None:
    """Configure Alembic and apply migrations on a synchronous connection.

    Used as the ``run_sync`` callback so DDL executes on the driver's sync
    connection while the surrounding stack stays async.

    Args:
        connection (sqlalchemy.engine.Connection): Sync connection passed by
            ``run_sync``.

    Returns:
        None

    """
    context.configure(
        connection=connection,
        target_metadata=mapper_registry.metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Acquire an async engine connection and run migrations via ``run_sync``.

    Closes the shared ``AsyncDatabaseClient`` after migrations finish.

    Returns:
        None

    """
    async with db_client.engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await db_client.close()


def run_migrations_online() -> None:
    """Entry point for Alembic online mode using ``asyncio.run``.

    Returns:
        None

    """
    asyncio.run(run_async_migrations())


run_migrations_online()
