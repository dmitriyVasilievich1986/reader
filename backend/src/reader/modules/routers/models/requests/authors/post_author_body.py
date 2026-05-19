"""Post author body model."""

__all__ = ("PostAuthorBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PostAuthorBody(BaseRequestModel):
    """Body model for creating an author."""

    first_name: str = Field(..., description="The first name of the author", min_length=1, max_length=255)
    last_name: str | None = Field(None, description="The last name of the author", min_length=1, max_length=255)
    cover: str | None = Field(None, description="The cover of the author")
