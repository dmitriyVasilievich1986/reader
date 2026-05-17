"""Get all books response model."""

__all__ = ("GetAllBooksResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.modules.routers.models.base.metadata import PaginationMetadata

from .simple_book_response import SimpleBookResponse


class GetAllBooksResponse(BaseResponseFromModelSchema):
    """Response model for getting all books."""

    data: list[SimpleBookResponse] = Field(..., description="The list of books")
    metadata: PaginationMetadata = Field(..., description="The metadata for the pagination")
