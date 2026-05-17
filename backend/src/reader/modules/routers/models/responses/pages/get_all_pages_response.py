"""Get all pages response model."""

__all__ = ("GetAllPagesResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.modules.routers.models.base.metadata import PaginationMetadata

from .simple_page_response import SimplePageResponse


class GetAllPagesResponse(BaseResponseFromModelSchema):
    """Response model for getting all pages."""

    data: list[SimplePageResponse] = Field(..., description="The list of pages")
    metadata: PaginationMetadata = Field(..., description="The metadata for the pagination")
