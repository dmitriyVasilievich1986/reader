"""Get single book response model."""

__all__ = ("GetSingleBookResponse",)


from pydantic import Field

from reader.modules.routers.models.base import BaseDateModel, BaseResponseFromModelSchema
from reader.modules.routers.models.responses.authors.simple_author_response import SimpleAuthorResponse


class GetSingleBookResponse(BaseResponseFromModelSchema, BaseDateModel):
    """Response model for getting a single book."""

    id: int = Field(..., description="The ID of the book")
    name: str = Field(..., description="The name of the book")
    description: str | None = Field(None, description="The description of the book")
    cover: str | None = Field(None, description="The cover of the book")
    author_id: int = Field(..., description="The ID of the author of the book")
    watches_count: int = Field(..., description="The number of times the book has been watched")
    author: SimpleAuthorResponse = Field(..., description="The author of the book")
