"""Patch user body model."""

__all__ = ("PatchUserBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class PatchUserBody(BaseRequestModel):
    """Body model for patching a user."""

    first_name: str | None = Field(None, description="The first name of the user")
    last_name: str | None = Field(None, description="The last name of the user")
    photo_url: str | None = Field(None, description="The photo URL of the user")
