"""Filesystem paths configuration model."""

__all__ = ("PathsInfo",)

from pathlib import Path

from pydantic import BaseModel, Field


class PathsInfo(BaseModel):
    """Filesystem locations of the static files and tooling used by the application.

    Attributes:
        static (Path): Root directory of the frontend build output.
        alembic_ini (Path): Path to the Alembic configuration file.
        assets (Path): Directory with the built frontend assets, served at
            ``/assets``.
        index_html (Path): SPA entry HTML file returned for client-side routes.
        images (Path): Directory with book images, served at ``/images``.

    """

    alembic_ini: Path = Field(..., description="The path to the Alembic configuration file")
    static: Path = Field(..., description="The root directory of the frontend build output")
    assets: Path = Field(..., description="The directory with the built frontend assets")
    index_html: Path = Field(..., description="The SPA entry HTML file")
    images: Path = Field(..., description="The directory with book images")
