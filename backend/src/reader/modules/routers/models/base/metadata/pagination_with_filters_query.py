"""Query model for pagination."""

__all__ = ("PaginationWithFiltersQuery",)


from pydantic import Field, Json

from reader.utils.filter import Filter

from .pagination_query import PaginationQuery


class PaginationWithFiltersQuery[SortByType: str, ColumnType: str](PaginationQuery[SortByType]):
    """Query parameters for pagination with filters."""

    filters: Json[list[Filter[ColumnType]]] | None = Field(None, description="The filters to apply to the parameters")
