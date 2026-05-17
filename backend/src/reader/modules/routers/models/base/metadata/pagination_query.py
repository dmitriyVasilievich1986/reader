"""Query model for pagination."""

__all__ = ("PaginationQuery",)

from typing import Literal

from pydantic import Field

from ..query import BaseQueryModel


class PaginationQuery[SortByType: str](BaseQueryModel):
    """Query parameters for pagination."""

    limit: int = Field(default=100, ge=1, le=100, description="The number of items to return")
    offset: int = Field(default=0, ge=0, description="The number of items to skip")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="The order to sort the items by")
    sort_by: SortByType = Field(default="id", description="The field to sort the items by")  # type: ignore[assignment]
