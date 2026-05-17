"""Singleton-backed storage for loaded application configuration instances."""

__all__ = ("SettingsStorage",)

from typing import TYPE_CHECKING

from reader.utils.singleton import Singleton

if TYPE_CHECKING:
    from .base import BaseConfig


class SettingsStorage[ConfigType: "BaseConfig"](metaclass=Singleton):
    """Hold a single optional settings object for a given config type.

    Used with :meth:`BaseConfig.get_or_create` so configuration is resolved
    through one shared instance per process. ``ConfigType`` is the concrete
    ``BaseConfig`` subclass being stored.
    """

    _settings: ConfigType | None = None

    @property
    def settings(self) -> ConfigType | None:
        """Return the cached settings instance, if any.

        Returns:
            ConfigType | None: The stored settings, or ``None`` if unset or
                cleared.

        """
        return self._settings

    @settings.setter
    def settings(self, settings: ConfigType) -> None:
        """Store the given settings instance as the singleton value.

        Args:
            settings (ConfigType): Configuration object to cache.

        """
        self._settings = settings

    @settings.deleter
    def settings(self) -> None:
        """Clear the cached settings instance.

        Returns:
            None

        """
        self._settings = None
