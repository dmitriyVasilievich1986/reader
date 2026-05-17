"""Simple category response model."""

__all__ = ("SimpleCategoryResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema


class SimpleCategoryResponse(BaseResponseFromModelSchema):
    """Response model for a simple category."""

    id: int = Field(..., description="The ID of the category")
    name: str = Field(..., description="The name of the category")
