"""Dependency provider for database client."""

__all__ = ("get_db",)

from typing import Annotated

from fastapi import Depends

from reader.config.app_config import AppConfig
from reader.services.database import AsyncDatabaseClient

from .get_config import get_config


def get_db(
    app_config: Annotated[AppConfig, Depends(get_config)],
) -> AsyncDatabaseClient:
    """Dependency function that provides a singleton instance of AsyncDatabaseClient.

    Args:
        app_config: The application configuration.

    Returns:
        A singleton instance of AsyncDatabaseClient.

    """
    return AsyncDatabaseClient(app_config=app_config)
