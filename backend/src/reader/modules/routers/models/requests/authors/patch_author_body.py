"""Patch author body model."""

__all__ = ("PatchAuthorBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PatchAuthorBody(BaseRequestModel):
    """Body model for patching an author."""

    first_name: str | None = Field(None, description="The first name of the author")
    last_name: str | None = Field(None, description="The last name of the author")
    cover: str | None = Field(None, description="The cover of the author")
