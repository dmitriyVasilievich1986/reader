"""Get all authors response model."""

__all__ = ("GetAllAuthorsResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.modules.routers.models.base.metadata import PaginationMetadata

from .simple_author_response import SimpleAuthorResponse


class GetAllAuthorsResponse(BaseResponseFromModelSchema):
    """Response model for getting all authors."""

    data: list[SimpleAuthorResponse] = Field(..., description="The list of authors")
    metadata: PaginationMetadata = Field(..., description="The metadata for the pagination")
