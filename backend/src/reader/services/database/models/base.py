"""Base model module."""

__all__ = ("Base",)

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry
from sqlalchemy.schema import MetaData

mapper_registry = registry(metadata=MetaData())


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy models."""

    registry = mapper_registry
    metadata = mapper_registry.metadata


class DateTimeMixin(DeclarativeBase):
    """Mixin for datetime fields."""

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
