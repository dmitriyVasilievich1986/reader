"""Category book table model for the database."""

__all__ = ("CategoryBookTable",)

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CategoryBookTable(Base):
    """A table linking categories to books."""

    __tablename__ = "category_book_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("book.id"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))
