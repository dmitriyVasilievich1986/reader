"""Alembic migration: initial schema for categories, authors, books, and pages.

Revision ID: 8e3f5d72efaf
Revises:
Create Date: 2025-01-18 13:24:28.514963

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint

# revision identifiers, used by Alembic.
revision: str = "8e3f5d72efaf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables for categories, authors, books, pages, and book-category links.

    Returns:
        None.

    """
    op.create_table(
        "category",
        Column("id", Integer),
        Column("name", String, unique=True, nullable=False),
        Column("description", String),
        Column("cover", String, nullable=True),
        UniqueConstraint("name", name="uq_category_name"),
        PrimaryKeyConstraint("id", name="pk_category"),
    )
    op.create_table(
        "author",
        Column("id", Integer),
        Column("first_name", String),
        Column("last_name", String),
        Column("cover", String, nullable=True),
        PrimaryKeyConstraint("id", name="pk_author"),
    )
    op.create_table(
        "book",
        Column("id", Integer),
        Column("name", String, unique=True, nullable=False),
        Column("description", String),
        Column("author_id", Integer(), nullable=False),
        Column("cover", String, nullable=True),
        PrimaryKeyConstraint("id", name="pk_book"),
        ForeignKeyConstraint(
            ["author_id"],
            ["author.id"],
            name="fk_author_id",
        ),
    )
    op.create_table(
        "page",
        Column("id", Integer),
        Column("position", Integer, nullable=False),
        Column("cover", String, nullable=True),
        Column("book_id", Integer(), nullable=False),
        PrimaryKeyConstraint("id", name="pk_page"),
        ForeignKeyConstraint(
            ["book_id"],
            ["book.id"],
            name="fk_book_id",
        ),
    )
    op.create_table(
        "category_book_table",
        Column("id", Integer),
        Column("book_id", Integer(), nullable=False),
        Column("category_id", Integer(), nullable=False),
        PrimaryKeyConstraint("id", name="pk_category_book_table"),
        UniqueConstraint("book_id", "category_id", name="uq_book_category"),
        ForeignKeyConstraint(
            ["book_id"],
            ["book.id"],
            name="fk_book_id",
        ),
        ForeignKeyConstraint(
            ["category_id"],
            ["category.id"],
            name="fk_category_id",
        ),
    )


def downgrade() -> None:
    """Drop ``category``, ``author``, ``book``, and ``category_book_table``.

    Returns:
        None.

    """
    op.drop_table("category")
    op.drop_table("author")
    op.drop_table("book")
    op.drop_table("page")

    op.drop_table("category_book_table")
