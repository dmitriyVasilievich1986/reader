"""Dependencies for the Reader application."""

__all__ = ("admin_required", "get_config", "get_db", "user_authorized")

from .admin_required import admin_required
from .get_config import get_config
from .get_db import get_db
from .user_authorized import user_authorized
