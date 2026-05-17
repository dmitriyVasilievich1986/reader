"""Simple book response model."""

__all__ = ("SimpleBookResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema


class SimpleBookResponse(BaseResponseFromModelSchema):
    """Response model for a simple book."""

    id: int = Field(..., description="The ID of the book")
    name: str = Field(..., description="The name of the book")
    author_id: int = Field(..., description="The ID of the author of the book")
    description: str | None = Field(None, description="The description of the book")
    cover: str | None = Field(None, description="The cover of the book")
