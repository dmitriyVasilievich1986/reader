"""Add a unique ``slug`` column to ``book`` and backfill from names.

Adds ``slug``, fills values from slugified titles with numeric suffixes on
collisions, enforces uniqueness and not-null, and briefly drops/recreates
foreign keys so SQLite batch alterations can apply.

Revision ID: 92552180df13
Revises: b922d12d33b3
Create Date: 2026-05-19 12:26:48.585370

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from slugify import slugify
from sqlalchemy.sql import column, select, table, update

# revision identifiers, used by Alembic.
revision: str = "92552180df13"
down_revision: Union[str, None] = "b922d12d33b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

book = table("book", column("id"), column("name"), column("slug"))


def upgrade() -> None:
    """Add ``slug`` to ``book``, backfill, then constrain and index it.

    Temporarily drops ``page.fk_book_id`` and ``book.fk_author_id`` so the
    ``book`` table can be altered under SQLite batch mode, then restores them.

    Returns:
        None

    """
    op.add_column("book", sa.Column("slug", sa.String(), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(select(book.c.id, book.c.name)).fetchall()
    seen_slugs: dict[str, int] = {}
    for book_id, name in rows:
        base = slugify(name or "") or f"book-{book_id}"
        slug_value = base
        suffix = 1
        while slug_value in seen_slugs:
            slug_value = f"{base}-{suffix}"
            suffix += 1
        seen_slugs[slug_value] = book_id
        conn.execute(update(book).values(slug=slug_value).where(book.c.id == book_id))

    with op.batch_alter_table("page") as batch_op:
        batch_op.drop_constraint("fk_book_id", type_="foreignkey")

    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_constraint("fk_author_id", type_="foreignkey")

    with op.batch_alter_table("book") as batch_op:
        batch_op.create_unique_constraint("uq_book_slug", ["slug"])
        batch_op.create_index("idx_book_slug", ["slug"])
        batch_op.alter_column("slug", nullable=False)
        batch_op.create_foreign_key("fk_author_id", "author", ["author_id"], ["id"])

    with op.batch_alter_table("page") as batch_op:
        batch_op.create_foreign_key("fk_book_id", "book", ["book_id"], ["id"])


def downgrade() -> None:
    """Remove ``slug`` from ``book`` and restore prior FK wiring.

    Mirrors ``upgrade`` by dropping FKs before batch changes, then
    re-creating them.

    Returns:
        None

    """
    with op.batch_alter_table("page") as batch_op:
        batch_op.drop_constraint("fk_book_id", type_="foreignkey")

    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_constraint("fk_author_id", type_="foreignkey")

    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_constraint("uq_book_slug", type_="unique")
        batch_op.drop_index("idx_book_slug")
        batch_op.drop_column("slug")
        batch_op.create_foreign_key("fk_author_id", "author", ["author_id"], ["id"])

    with op.batch_alter_table("page") as batch_op:
        batch_op.create_foreign_key("fk_book_id", "book", ["book_id"], ["id"])
