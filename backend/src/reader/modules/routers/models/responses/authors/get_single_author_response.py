"""Get single author response model."""

__all__ = ("GetSingleAuthorResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.utils.models import DateModel


class GetSingleAuthorResponse(BaseResponseFromModelSchema, DateModel):
    """Response model for getting a single author."""

    id: int = Field(..., description="The ID of the author")
    first_name: str = Field(..., description="The first name of the author")
    last_name: str | None = Field(None, description="The last name of the author")
    cover: str | None = Field(None, description="The cover of the author")
