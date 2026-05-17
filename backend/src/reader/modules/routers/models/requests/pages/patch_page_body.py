"""Patch page body model."""

__all__ = ("PatchPageBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PatchPageBody(BaseRequestModel):
    """Body model for patching a page."""

    position: int | None = Field(None, description="The position of the page within the book")
    cover: str | None = Field(None, description="The cover of the page")
    book_id: int | None = Field(None, description="The ID of the book the page belongs to")
