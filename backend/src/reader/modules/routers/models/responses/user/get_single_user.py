"""Get single user response model."""

__all__ = ("GetSingleUserResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseDateModel, BaseResponseFromModelSchema


class GetSingleUserResponse(BaseResponseFromModelSchema, BaseDateModel):
    """Response model for getting a single user."""

    id: int = Field(..., description="The ID of the user")
    username: str = Field(..., description="The username of the user")
    email: str = Field(..., description="The email of the user")
    first_name: str | None = Field(None, description="The first name of the user")
    last_name: str | None = Field(None, description="The last name of the user")
    photo_url: str | None = Field(None, description="The photo URL of the user")
    is_active: bool = Field(..., description="Whether the user is active")
