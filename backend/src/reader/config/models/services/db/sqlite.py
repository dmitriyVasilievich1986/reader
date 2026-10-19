"""SQLite database configuration model."""

__all__ = ("SQLite",)

from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class SQLite(BaseModel):
    """SQLite database connection configuration.

    Attributes:
        provider (Literal["sqlite+aiosqlite"]): SQLAlchemy dialect and driver.
            Defaults to ``"sqlite+aiosqlite"``.
        host (SecretStr): Path to the SQLite database file.

    """

    provider: Literal["sqlite+aiosqlite"] = Field("sqlite+aiosqlite", description="The provider of the database")
    host: SecretStr = Field(..., description="The host of the database")

    @property
    def url(self) -> URL:
        """Build the SQLAlchemy connection URL for the SQLite database.

        Returns:
            URL: Connection URL pointing at the configured database file.

        """
        return URL.create(self.provider, database=self.host.get_secret_value())
