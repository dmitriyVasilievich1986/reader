"""Database connection configuration model.

This module defines the configuration model for database connections, supporting
multiple async database providers (SQLite with aiosqlite and PostgreSQL with
asyncpg) and generating SQLAlchemy async connection URLs.
"""

__all__ = ("Database",)

from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class Database(BaseModel):
    """Configuration model for async database connection settings.

    This model handles database connection configuration for different async
    providers, including SQLite with aiosqlite for local development and
    PostgreSQL with asyncpg for production. It securely manages credentials
    using Pydantic's SecretStr and generates SQLAlchemy async connection URLs.

    Attributes:
        provider: The async database provider type. Must be either
            "sqlite+aiosqlite" (SQLite with async driver) or
            "postgresql+asyncpg" (PostgreSQL with async driver).
            This is a required field.
        host: The database host. For SQLite, this is the file path to the
            database file. For PostgreSQL, this is the hostname or IP address
            of the database server. This is a required field.
        port: The port number for the database connection. Only used for
            PostgreSQL. Defaults to None (uses provider default, typically 5432).
        name: The name of the database. Only used for PostgreSQL. For SQLite,
            the database name is part of the host path. Defaults to None.
        user: The username for database authentication. Only used for
            PostgreSQL. Stored securely as SecretStr. Defaults to None.
        password: The password for database authentication. Only used for
            PostgreSQL. Stored securely as SecretStr. Defaults to None.

    Properties:
        url: Generates a SQLAlchemy URL object for the configured async
            database connection.

    Raises:
        ValueError: If an invalid database provider is specified.

    Example:
        SQLite with aiosqlite configuration:
        >>> db = Database(provider="sqlite+aiosqlite", host="./reader.sqlite3")
        >>> print(db.url)
        sqlite+aiosqlite:///./reader.sqlite3

        PostgreSQL with asyncpg configuration:
        >>> db = Database(
        ...     provider="postgresql+asyncpg",
        ...     host="localhost",
        ...     port=5432,
        ...     name="reader_db",
        ...     user=SecretStr("dbuser"),
        ...     password=SecretStr("dbpass")
        ... )

    """

    provider: Literal["sqlite+aiosqlite", "postgresql+asyncpg"] = Field(..., description="The provider of the database")
    host: str = Field(..., description="The host of the database")

    port: int | None = Field(None, description="The port of the database")
    name: str | None = Field(None, description="The name of the database")
    user: SecretStr | None = Field(None, description="The user of the database")
    password: SecretStr | None = Field(None, description="The password of the database")

    @property
    def url(self) -> URL:
        """Generate a SQLAlchemy URL for the async database connection.

        Creates a SQLAlchemy URL object based on the configured async provider
        and connection parameters. For SQLite with aiosqlite, only the database
        file path is used. For PostgreSQL with asyncpg, all connection parameters
        including credentials are included.

        Returns:
            URL: A SQLAlchemy URL object that can be used to create async database
                engine connections.

        Raises:
            ValueError: If the provider is not "sqlite+aiosqlite" or
                "postgresql+asyncpg".

        """
        match self.provider:
            case "sqlite+aiosqlite":
                return URL.create(self.provider, database=self.host)
            case "postgresql+asyncpg" | "postgresql+psycopg":
                if not any((self.user, self.password, self.name)):
                    raise ValueError("User, password and name are required for PostgreSQL")
                return URL.create(
                    self.provider,
                    username=self.user.get_secret_value(),  # type: ignore[union-attr]
                    password=self.password.get_secret_value(),  # type: ignore[union-attr]
                    host=self.host,
                    port=self.port,
                    database=self.name,
                )
            case _:
                raise ValueError(f"Invalid database provider: {self.provider}")
