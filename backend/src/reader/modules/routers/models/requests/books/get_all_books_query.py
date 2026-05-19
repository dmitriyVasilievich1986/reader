"""Get all books query model."""

__all__ = ("GetAllBooksQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllBooksQuery(
    PaginationWithFiltersQuery[
        Literal["id", "name", "author_id", "created_at", "updated_at", "watches_count", "slug"],
        Literal["id", "name", "author_id", "created_at", "updated_at", "watches_count", "slug"],
    ]
):
    """Query model for getting all books."""

    pass
