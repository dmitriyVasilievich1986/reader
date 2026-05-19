"""Post page body model."""

__all__ = ("PostPageBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PostPageBody(BaseRequestModel):
    """Body model for creating a page."""

    position: int = Field(..., description="The position of the page within the book", ge=1)
    cover: str | None = Field(None, description="The cover of the page")
    book_id: int = Field(..., description="The ID of the book the page belongs to")
