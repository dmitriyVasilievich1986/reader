"""Add ``created_at`` and ``updated_at`` columns to core tables.

Adds non-null UTC datetime columns for creation and last-update timestamps
on ``author``, ``book``, ``category``, ``page``, and ``user``.

Revision ID: ca414c66f0fa
Revises: 14ba01e0e048
Create Date: 2026-05-18 22:07:27.120311

"""

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision: str = "ca414c66f0fa"
down_revision: Union[str, None] = "14ba01e0e048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PLACED_HOLDER_TIMESTAMP: str = str(datetime.now(timezone.utc))

author = table("author", column("created_at"), column("updated_at"))
book = table("book", column("created_at"), column("updated_at"))
category = table("category", column("created_at"), column("updated_at"))
page = table("page", column("created_at"), column("updated_at"))
user = table("user", column("created_at"), column("updated_at"))


def upgrade() -> None:
    """Add ``created_at`` and ``updated_at`` columns to each affected table.

    Returns:
        None

    """
    op.add_column(
        "author", sa.Column("created_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP)
    )
    op.add_column(
        "author", sa.Column("updated_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP)
    )

    op.add_column("book", sa.Column("created_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))
    op.add_column("book", sa.Column("updated_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))

    op.add_column(
        "category", sa.Column("created_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP)
    )
    op.add_column(
        "category", sa.Column("updated_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP)
    )

    op.add_column("page", sa.Column("created_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))
    op.add_column("page", sa.Column("updated_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))

    op.add_column("user", sa.Column("created_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))
    op.add_column("user", sa.Column("updated_at", sa.DateTime, nullable=False, server_default=PLACED_HOLDER_TIMESTAMP))

    op.execute(author.update().values(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
    op.execute(book.update().values(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
    op.execute(category.update().values(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
    op.execute(page.update().values(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
    op.execute(user.update().values(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))


def downgrade() -> None:
    """Drop ``created_at`` and ``updated_at`` columns from each affected table.

    Returns:
        None

    """
    op.drop_column("author", "created_at")
    op.drop_column("author", "updated_at")

    op.drop_column("book", "created_at")
    op.drop_column("book", "updated_at")

    op.drop_column("category", "created_at")
    op.drop_column("category", "updated_at")

    op.drop_column("page", "created_at")
    op.drop_column("page", "updated_at")

    op.drop_column("user", "created_at")
    op.drop_column("user", "updated_at")
