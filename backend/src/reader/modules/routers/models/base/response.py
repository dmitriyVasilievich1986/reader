"""Base response model for web API."""

__all__ = ("BaseResponseModel",)

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseResponseModel(BaseModel):
    """Base model for all response models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_alias=False,
    )


class BaseResponseFromModelSchema(BaseModel):
    """Base schema for all response models from model schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_alias=False,
    )
