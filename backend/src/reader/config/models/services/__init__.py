"""Service configuration models.

This module provides configuration models for external services used by the
application, such as database connections. It aggregates service-specific
configuration into a unified Services model.
"""

__all__ = ("Services",)

from pydantic import BaseModel, Field

from .auth import Auth
from .database import Database


class Services(BaseModel):
    """Container for all external service configurations.

    This model aggregates configuration settings for various external services
    that the application depends on, such as databases, caches, message queues,
    etc. Currently includes database configuration.

    Attributes:
        database: Configuration settings for the database connection, including
            provider type, connection parameters, and credentials.

    """

    database: Database = Field(..., description="The database service")
    auth: Auth = Field(..., description="The auth service")
