"""Pydantic model for an author."""

__all__ = ("Author",)

from pydantic import BaseModel, Field


class Author(BaseModel):
    """Author model with first name and last name."""

    first_name: str = Field(..., description="The first name of the author")
    last_name: str | None = Field(None, description="The last name of the author")
