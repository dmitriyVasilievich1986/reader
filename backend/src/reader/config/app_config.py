"""Root application configuration model."""

__all__ = ("AppConfig",)


from typing import Literal

from pydantic import Field

from .base import BaseConfig
from .models import Info, Services


class AppConfig(BaseConfig):
    """Top-level settings for the Reader application.

    Aggregates application metadata and service settings loaded from YAML
    and environment overrides via ``BaseConfig``.

    Attributes:
        environment (Literal["local", "prod", "test"]): Environment the
            application runs in. Defaults to ``"prod"``.
        info (Info): Application metadata, API server, CORS and path settings.
        services (Services): Configuration of downstream services such as the
            database and auth.

    """

    environment: Literal["local", "prod", "test"] = Field(
        "prod",
        description="The environment the application runs in",
    )

    info: Info = Field(..., description="The information of the application")
    services: Services = Field(..., description="The services of the application")

    @property
    def is_local(self) -> bool:
        """Check whether the application runs in the local environment.

        Returns:
            bool: True if ``environment`` is ``"local"``.

        """
        return self.environment == "local"

    @property
    def is_test(self) -> bool:
        """Check whether the application runs in the test environment.

        Returns:
            bool: True if ``environment`` is ``"test"``.

        """
        return self.environment == "test"

    @property
    def is_prod(self) -> bool:
        """Check whether the application runs in the production environment.

        Returns:
            bool: True if ``environment`` is ``"prod"``.

        """
        return self.environment == "prod"
