"""Filesystem path configuration for the application.

Defines ``PathsInfo``, which resolves standard directories under the backend
package root (``static``, bundled frontend output, images, fonts, Alembic).
"""

__all__ = ("PathsInfo",)

from pathlib import Path

from pydantic import BaseModel, Field


class PathsInfo(BaseModel):
    """Resolved paths for backend assets and application sources.

    The default ``root`` is the ``backend/`` directory (inferred from this
    module's path via ``parents[5]``), so paths stay correct regardless of
    the process working directory.

    Attributes:
        root: Backend package root (parent of ``src/`` and ``static/``).

    """

    root: Path = Field(
        Path(__file__).resolve().parents[5],
        description="Backend package root (directory containing src/ and static/).",
    )

    @property
    def static(self) -> Path:
        """Return the static files root directory.

        Returns:
            Path: ``root / "static"``.

        """
        return self.root / "static"

    @property
    def src(self) -> Path:
        """Return the ``reader`` Python package directory.

        Returns:
            Path: ``root / "src" / "reader"``.

        """
        return self.root / "src" / "reader"

    @property
    def assets(self) -> Path:
        """Return the directory for bundled frontend assets (e.g. JS/CSS).

        Returns:
            Path: ``static / "assets"``.

        """
        return self.static / "assets"

    @property
    def index_html(self) -> Path:
        """Return the index.html file.

        Returns:
            Path: ``static / "index.html"``.

        """
        return self.static / "index.html"

    @property
    def js(self) -> Path:
        """Return the directory for bundled JavaScript assets.

        Returns:
            Path: ``static / "js"``.

        """
        return self.static / "js"

    @property
    def css(self) -> Path:
        """Return the directory for stylesheet assets.

        Returns:
            Path: ``static / "css"``.

        """
        return self.static / "css"

    @property
    def images(self) -> Path:
        """Return the directory for image assets.

        Returns:
            Path: ``static / "images"``.

        """
        return self.static / "images"

    @property
    def fonts(self) -> Path:
        """Return the directory for font assets.

        Returns:
            Path: ``static / "fonts"``.

        """
        return self.static / "fonts"

    @property
    def alembic_ini(self) -> Path:
        """Return the Alembic configuration file path.

        Returns:
            Path: ``src / "services" / "alembic" / "alembic.ini"``.

        """
        return self.src / "services" / "alembic" / "alembic.ini"
