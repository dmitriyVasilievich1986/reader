"""SQLAlchemy models backing the Reader catalog."""

__all__ = ("Author", "Book", "Category", "Page")

from flask_appbuilder import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

metadata = Model.metadata


class Category(Model):
    """A tag-like shelf used to classify books."""

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")


class Author(Model):
    """A writer credited on one or more books."""

    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")

    @property
    def name(self) -> str:
        """Return ``first_name`` followed by ``last_name`` separated by one space.

        Returns:
            str: Concatenated author name text.

        """
        return f"{self.first_name} {self.last_name}"


CategoryBookTables = Table(
    "category_book_tables",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)


class Book(Model):
    """Published work keyed by ``name`` with author, categories, and pages."""

    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")

    author_id = Column(Integer, ForeignKey("author.id"))

    author = relationship(Author, backref="book", foreign_keys=[author_id])
    categories = relationship(
        Category,
        secondary=CategoryBookTables,
        backref="row_level_security_filters",
    )

    @property
    def author_name(self) -> str:
        """Return ``Author.name`` for the owning author relation.

        Returns:
            str: Full author name from the linked ``Author``.

        """
        return self.author.name


class Page(Model):
    """Ordered image reference belonging to exactly one ``Book``."""

    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    cover = Column(String, default="/static/i/noimage.jpg")

    book_id = Column(Integer, ForeignKey("book.id"))
    book = relationship(Book, backref="page", foreign_keys=[book_id])
