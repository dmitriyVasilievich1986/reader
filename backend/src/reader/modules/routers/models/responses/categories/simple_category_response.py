"""Simple category response model."""

__all__ = ("SimpleCategoryResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseDateModel, BaseResponseFromModelSchema


class SimpleCategoryResponse(BaseResponseFromModelSchema, BaseDateModel):
    """Response model for a simple category."""

    id: int = Field(..., description="The ID of the category")
    name: str = Field(..., description="The name of the category")
    description: str | None = Field(None, description="The description of the category")
    cover: str | None = Field(None, description="The cover of the category")
