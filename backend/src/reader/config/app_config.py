"""App config module."""

__all__ = ("AppConfig",)


from pydantic import Field

from .base import BaseConfig
from .models import Info, Services


class AppConfig(BaseConfig):
    """Application configuration settings.

    This class holds all application-level configuration settings including
    allowed hosts, secret key, debug mode, and database connection settings.
    Supports both SQLite and PostgreSQL database engines.
    """

    info: Info = Field(..., description="The information of the application")
    services: Services = Field(..., description="The services of the application")
