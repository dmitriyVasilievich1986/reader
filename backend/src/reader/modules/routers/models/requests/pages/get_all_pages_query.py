"""Get all pages query model."""

__all__ = ("GetAllPagesQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllPagesQuery(
    PaginationWithFiltersQuery[
        Literal["id", "position", "book_id", "created_at", "updated_at"],
        Literal["id", "position", "book_id", "created_at", "updated_at"],
    ]
):
    """Query model for getting all pages."""

    pass
