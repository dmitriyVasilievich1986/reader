"""Patch book body model."""

__all__ = ("PatchBookBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PatchBookBody(BaseRequestModel):
    """Body model for patching a book."""

    name: str | None = Field(None, description="The name of the book")
    description: str | None = Field(None, description="The description of the book")
    cover: str | None = Field(None, description="The cover of the book")
    author_id: int | None = Field(None, description="The ID of the author of the book")
