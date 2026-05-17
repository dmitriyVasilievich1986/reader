"""Patch category body model."""

__all__ = ("PatchCategoryBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PatchCategoryBody(BaseRequestModel):
    """Body model for patching a category."""

    name: str | None = Field(None, description="The name of the category")
    description: str | None = Field(None, description="The description of the category")
    cover: str | None = Field(None, description="The cover of the category")
