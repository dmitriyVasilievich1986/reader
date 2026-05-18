"""Routers module."""

__all__ = ("api_router", "index_router")

from .api import router as api_router
from .index import router as index_router
