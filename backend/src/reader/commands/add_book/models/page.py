"""Pydantic model for a page."""

__all__ = ("Page",)

from pathlib import Path

from pydantic import BaseModel, Field


class Page(BaseModel):
    """Page model with path, position and cover."""

    path: Path = Field(..., description="The path to the page")
    position: int = Field(..., description="The position of the page within the book", ge=1)
    cover: str = Field(..., description="The cover of the page")
