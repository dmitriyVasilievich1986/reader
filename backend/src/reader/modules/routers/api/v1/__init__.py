"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .authors import router as authors_router
from .books import router as books_router
from .categories import router as categories_router
from .pages import router as pages_router
from .user import router as user_router

router = APIRouter(prefix="/v1")

router.include_router(authors_router)
router.include_router(books_router)
router.include_router(categories_router)
router.include_router(pages_router)
router.include_router(user_router)
