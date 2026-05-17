"""Get all books query model."""

__all__ = ("GetAllBooksQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllBooksQuery(
    PaginationWithFiltersQuery[
        Literal["id", "name", "author_id"],
        Literal["id", "name", "author_id"],
    ]
):
    """Query model for getting all books."""

    pass
