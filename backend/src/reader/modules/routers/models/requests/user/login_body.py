"""Login body model."""

__all__ = ("LoginBody",)

from pydantic import Field

from reader.modules.routers.models.base import BaseRequestModel


class LoginBody(BaseRequestModel):
    """Login body model."""

    username: str = Field(..., description="The username of the user")
    password: str = Field(..., description="The password of the user")
