"""Application lifespan management for FastAPI."""

__all__ = ("lifespan",)

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from reader.config.app_config import AppConfig
from reader.services.database import AsyncDatabaseClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the application lifecycle, initializing and cleaning up services.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control returns to the application during its lifetime.

    Raises:
        ConnectionError: If unable to connect to services.
        Exception: If services fail to initialize.

    """
    logger.info("Starting application lifespan...")
    logger.info(f"Debug mode: {app.debug}")

    # Initialize services
    logger.info("Initializing Database client...")
    app_config = AppConfig.get_or_create()
    database_client = AsyncDatabaseClient(app_config=app_config)
    logger.info("Database client initialized successfully.")

    yield

    # Cleanup
    logger.info("Shutting down application lifespan...")
    await database_client.close()
    logger.info("Database client closed successfully.")
