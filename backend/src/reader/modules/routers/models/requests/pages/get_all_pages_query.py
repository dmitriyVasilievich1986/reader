"""Get all pages query model."""

__all__ = ("GetAllPagesQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllPagesQuery(
    PaginationWithFiltersQuery[
        Literal["id", "position", "book_id"],
        Literal["id", "position", "book_id"],
    ]
):
    """Query model for getting all pages."""

    pass
