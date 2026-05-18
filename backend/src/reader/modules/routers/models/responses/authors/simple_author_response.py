"""Simple author response model."""

__all__ = ("SimpleAuthorResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseFromModelSchema
from reader.utils.models import DateModel


class SimpleAuthorResponse(BaseResponseFromModelSchema, DateModel):
    """Response model for a simple author."""

    id: int = Field(..., description="The ID of the author")
    first_name: str = Field(..., description="The first name of the author")
    last_name: str | None = Field(None, description="The last name of the author")
    cover: str | None = Field(None, description="The cover of the author")
