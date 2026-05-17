"""Dependency provider for application settings."""

__all__ = ("get_config",)

from reader.config.app_config import AppConfig


def get_config() -> AppConfig:
    """Dependency function that provides a singleton instance of AppConfig.

    Returns:
        A singleton instance of AppConfig.

    """
    return AppConfig.get_or_create()
