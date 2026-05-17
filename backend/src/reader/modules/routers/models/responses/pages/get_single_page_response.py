"""Get single page response model."""

__all__ = ("GetSinglePageResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.modules.routers.models.responses.books.simple_book_response import SimpleBookResponse


class GetSinglePageResponse(BaseResponseFromModelSchema):
    """Response model for getting a single page."""

    id: int = Field(..., description="The ID of the page")
    position: int = Field(..., description="The position of the page within the book")
    cover: str | None = Field(None, description="The cover of the page")
    book_id: int = Field(..., description="The ID of the book the page belongs to")
    book: SimpleBookResponse = Field(..., description="The book the page belongs to")
