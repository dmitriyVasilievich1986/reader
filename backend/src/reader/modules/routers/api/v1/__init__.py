"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

router = APIRouter(prefix="/v1")
