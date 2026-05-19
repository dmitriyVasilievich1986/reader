"""Post book body model."""

__all__ = ("PostBookBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PostBookBody(BaseRequestModel):
    """Body model for creating a book."""

    name: str = Field(..., description="The name of the book", min_length=1, max_length=255)
    description: str | None = Field(None, description="The description of the book", min_length=1, max_length=1000)
    cover: str | None = Field(None, description="The cover of the book")
    author_id: int = Field(..., description="The ID of the author of the book")
