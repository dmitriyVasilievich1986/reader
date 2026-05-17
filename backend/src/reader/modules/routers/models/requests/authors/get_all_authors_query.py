"""Get all authors query model."""

__all__ = ("GetAllAuthorsQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllAuthorsQuery(
    PaginationWithFiltersQuery[
        Literal["id", "first_name", "last_name"],
        Literal["id", "first_name", "last_name"],
    ]
):
    """Query model for getting all authors."""

    pass
