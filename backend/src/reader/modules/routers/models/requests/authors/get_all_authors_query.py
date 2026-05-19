"""Get all authors query model."""

__all__ = ("GetAllAuthorsQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllAuthorsQuery(
    PaginationWithFiltersQuery[
        Literal["id", "first_name", "last_name", "created_at", "updated_at"],
        Literal["id", "first_name", "last_name", "created_at", "updated_at"],
    ]
):
    """Query model for getting all authors."""

    pass
