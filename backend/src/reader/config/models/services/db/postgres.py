"""PostgreSQL database configuration model."""

__all__ = ("Postgres",)

from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class Postgres(BaseModel):
    """PostgreSQL database connection configuration.

    Attributes:
        provider (Literal["postgresql+asyncpg"]): SQLAlchemy dialect and driver.
        host (str): Hostname of the database server.
        port (int): Port of the database server. Defaults to ``5432``.
        name (str): Name of the database. Defaults to ``"reader"``.
        user (SecretStr): Username used to connect to the database.
        password (SecretStr): Password used to connect to the database.

    """

    provider: Literal["postgresql+asyncpg"] = Field(..., description="The provider of the database")
    host: str = Field(..., description="The host of the database")

    port: int = Field(5432, description="The port of the database")
    name: str = Field("reader", description="The name of the database")

    user: SecretStr = Field(..., description="The user of the database")
    password: SecretStr = Field(..., description="The password of the database")

    @property
    def url(self) -> URL:
        """Build the SQLAlchemy connection URL for the PostgreSQL database.

        Returns:
            URL: Connection URL built from the configured credentials, host,
                port and database name.

        """
        return URL.create(
            self.provider,
            username=self.user.get_secret_value(),
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
        )
