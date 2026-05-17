"""Base config module."""

__all__ = ("BaseConfig",)

from os import getenv
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from .storage import SettingsStorage


class BaseConfig(BaseSettings):
    """Base configuration class for application settings.

    This class extends Pydantic's BaseSettings to provide a foundation for
    configuration classes. It supports loading settings from .env files with
    nested configuration support and implements a singleton-like pattern
    through the get_or_create class method.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize the sources from which settings are loaded.

        This method overrides Pydantic's default settings sources to include
        a YAML configuration file as an additional source. The YAML file path
        is determined by the CONFIG_FILE_PATH environment variable, defaulting
        to "configurations/prod.yaml" if not set.

        The priority order of settings sources (highest to lowest) is:
        1. Initialization settings (arguments passed to __init__)
        2. Environment variables
        3. .env file settings
        4. File secret settings
        5. YAML configuration file

        Args:
            settings_cls: The settings class being configured.
            init_settings: Settings passed during class initialization.
            env_settings: Settings loaded from environment variables.
            dotenv_settings: Settings loaded from .env file.
            file_secret_settings: Settings loaded from secret files.

        Returns:
            tuple[PydanticBaseSettingsSource, ...]: A tuple of settings sources
                in priority order.

        Raises:
            FileNotFoundError: If the specified YAML configuration file does
                not exist.

        """
        file_path = Path(getenv("CONFIG_FILE_PATH", "configurations/prod.yaml"))
        if not file_path.exists():
            logger.warning(f"Config file path {file_path} does not exist. Aborting.")
            raise FileNotFoundError(f"Config file path {file_path} does not exist.")

        sources = [
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file=file_path),
        ]

        return tuple(filter(None, sources))

    @classmethod
    def get_or_create(cls, reload: bool = False) -> Self:
        """Get existing settings instance or create a new one.

        This method implements a singleton-like pattern by storing the settings
        instance in SettingsStorage. If an instance already exists and reload
        is False, it returns the existing instance. Otherwise, it creates a new
        instance and stores it.

        Args:
            reload: If True, forces creation of a new settings instance even
                if one already exists. Defaults to False.

        Returns:
            Self: An instance of the configuration class.

        """
        storage = SettingsStorage[Self]()

        if not reload and storage.settings:
            return storage.settings

        settings = cls()
        storage.settings = settings
        return settings
