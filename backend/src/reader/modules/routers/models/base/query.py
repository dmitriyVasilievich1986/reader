"""Base query model for web API."""

__all__ = ("BaseQueryModel",)

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseQueryModel(BaseModel):
    """Base model for all query models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=False,
        validate_by_alias=True,
        populate_by_name=True,
    )
