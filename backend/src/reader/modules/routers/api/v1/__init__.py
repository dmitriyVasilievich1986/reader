"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .categories import router as categories_router

router = APIRouter(prefix="/v1")

router.include_router(categories_router)
