"""Get all categories query model."""

__all__ = ("GetAllCategoriesQuery",)

from typing import Literal

from reader.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllCategoriesQuery(PaginationWithFiltersQuery[Literal["id", "name"], Literal["id", "name"]]):
    """Query model for getting all categories."""

    pass
