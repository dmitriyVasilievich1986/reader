"""API router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .system import router as system_router
from .v1 import router as v1_router

router = APIRouter(prefix="/api")

router.include_router(v1_router)
router.include_router(system_router)
