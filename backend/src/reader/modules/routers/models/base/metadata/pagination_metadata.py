"""Metadata model for the web API."""

__all__ = ("PaginationMetadata",)


from pydantic import Field

from reader.utils.models.filter import Filter

from ..response import BaseResponseModel


class PaginationMetadata(BaseResponseModel):
    """Metadata for paginated list responses.

    Exposes the total number of records matching the query and echoes the
    offset, limit, and sort parameters that were applied.
    """

    total: int = Field(..., description="The total number of parameters")
    offset: int | None = Field(..., description="The offset of the parameters")
    limit: int | None = Field(..., description="The limit of the parameters")
    sort_by: str = Field(..., description="The field to sort the parameters by")
    sort_order: str = Field(..., description="The order to sort the parameters by")
    filters: list[Filter[str]] | None = Field(..., description="The filters to apply to the parameters")
