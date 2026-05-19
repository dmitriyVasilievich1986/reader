"""Utility functions for the Reader application."""

__all__ = ("Filter", "Singleton", "mount_static_files")

from .models import Filter
from .mount_static_files import mount_static_files
from .singleton import Singleton
