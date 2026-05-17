"""Root application configuration model."""

__all__ = ("AppConfig",)


from pydantic import Field

from .base import BaseConfig
from .models import Info, Services


class AppConfig(BaseConfig):
    """Top-level settings for the Reader application.

    Aggregates descriptive metadata and service endpoints loaded from YAML
    and environment overrides via BaseConfig.

    Attributes:
        info (Info): Static application identification and versioning.
        services (Services): Configuration for downstream services such as the
            database.

    """

    info: Info = Field(..., description="The information of the application")
    services: Services = Field(..., description="The services of the application")
