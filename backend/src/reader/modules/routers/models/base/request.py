"""Base request model for web API."""

__all__ = ("BaseRequestModel",)

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseRequestModel(BaseModel):
    """Base model for all request models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=False,
        validate_by_alias=True,
        populate_by_name=True,
    )
