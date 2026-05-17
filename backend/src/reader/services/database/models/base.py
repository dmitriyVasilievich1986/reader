"""Base model module."""

__all__ = ("Base",)

from sqlalchemy.orm import DeclarativeBase, registry
from sqlalchemy.schema import MetaData

mapper_registry = registry(metadata=MetaData())


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy models."""

    registry = mapper_registry
    metadata = mapper_registry.metadata
