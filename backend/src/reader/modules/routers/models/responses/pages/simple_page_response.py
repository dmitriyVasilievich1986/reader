"""Simple page response model."""

__all__ = ("SimplePageResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseDateModel, BaseResponseFromModelSchema


class SimplePageResponse(BaseResponseFromModelSchema, BaseDateModel):
    """Response model for a simple page."""

    id: int = Field(..., description="The ID of the page")
    position: int = Field(..., description="The position of the page within the book")
    cover: str | None = Field(None, description="The cover of the page")
    book_id: int = Field(..., description="The ID of the book the page belongs to")
