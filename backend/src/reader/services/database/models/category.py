"""Category model for the database."""

__all__ = ("Category",)

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .book import Book


class Category(Base):
    """A tag-like shelf used to classify books."""

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    cover: Mapped[str | None] = mapped_column(String, nullable=True)

    books: Mapped[list["Book"]] = relationship("Book", secondary="category_book_table", back_populates="categories")
