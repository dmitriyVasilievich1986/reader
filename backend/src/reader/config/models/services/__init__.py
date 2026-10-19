"""Configuration models for the external services used by the application."""

__all__ = ("Services",)

from pydantic import BaseModel, Field

from .auth import Auth
from .db import Postgres, SQLite


class Services(BaseModel):
    """Configuration of all services the application depends on.

    Attributes:
        database (SQLite | Postgres): Database connection settings.
        auth (Auth): JWT authentication settings.

    """

    database: SQLite | Postgres = Field(..., description="The database service")
    auth: Auth = Field(..., description="The auth service")
