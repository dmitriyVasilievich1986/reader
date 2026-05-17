"""Post category body model."""

__all__ = ("PostCategoryBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PostCategoryBody(BaseRequestModel):
    """Body model for creating a category."""

    name: str = Field(..., description="The name of the category")
    description: str | None = Field(None, description="The description of the category")
    cover: str | None = Field(None, description="The cover of the category")
