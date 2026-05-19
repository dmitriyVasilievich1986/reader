"""Post category body model."""

__all__ = ("PostCategoryBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PostCategoryBody(BaseRequestModel):
    """Body model for creating a category."""

    name: str = Field(..., description="The name of the category", min_length=1, max_length=255)
    description: str | None = Field(None, description="The description of the category", min_length=1, max_length=1000)
    cover: str | None = Field(None, description="The cover of the category")
