"""Get all categories response model."""

__all__ = ("GetAllCategoriesResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.modules.routers.models.base.metadata import PaginationMetadata

from .simple_category_response import SimpleCategoryResponse


class GetAllCategoriesResponse(BaseResponseFromModelSchema):
    """Response model for getting all categories."""

    data: list[SimpleCategoryResponse] = Field(..., description="The list of categories")
    metadata: PaginationMetadata = Field(..., description="The metadata for the pagination")
