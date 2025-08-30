"""init

Revision ID: 8e3f5d72efaf
Revises:
Create Date: 2025-01-18 13:24:28.514963

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import Column, ForeignKeyConstraint, Integer, String, UniqueConstraint

# revision identifiers, used by Alembic.
revision: str = "8e3f5d72efaf"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "category",
        Column("id", Integer, primary_key=True),
        Column("name", String, unique=True, nullable=False),
        Column("description", String),
        Column("cover", String, default="/static/i/noimage.jpg"),
    )
    op.create_table(
        "author",
        Column("id", Integer, primary_key=True),
        Column("first_name", String),
        Column("last_name", String),
        Column("cover", String, default="/static/i/noimage.jpg"),
    )
    op.create_table(
        "book",
        Column("id", Integer, primary_key=True),
        Column("name", String, unique=True, nullable=False),
        Column("description", String),
        Column("author_id", Integer(), nullable=False),
        Column("cover", String, default="/static/i/noimage.jpg"),
        ForeignKeyConstraint(
            ["author_id"],
            ["author.id"],
            name="fk_author_id",
        ),
    )
    op.create_table(
        "page",
        Column("id", Integer, primary_key=True),
        Column("position", Integer, nullable=False),
        Column("cover", String, default="/static/i/noimage.jpg"),
        Column("book_id", Integer(), nullable=False),
        ForeignKeyConstraint(
            ["book_id"],
            ["book.id"],
            name="fk_book_id",
        ),
    )
    op.create_table(
        "category_book_tables",
        Column("book_id", Integer(), nullable=False),
        Column("category_id", Integer(), nullable=False),
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
        UniqueConstraint("book_id", "category_id", name="uq_book_category"),
    )


def downgrade() -> None:
    op.drop_table("category")
    op.drop_table("author")
    op.drop_table("book")

    op.drop_table("category_book_tables")
