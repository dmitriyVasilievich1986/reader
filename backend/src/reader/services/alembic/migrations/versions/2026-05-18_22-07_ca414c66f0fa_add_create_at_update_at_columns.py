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

# revision identifiers, used by Alembic.
revision: str = "ca414c66f0fa"
down_revision: Union[str, None] = "14ba01e0e048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ``created_at`` and ``updated_at`` columns to each affected table.

    Returns:
        None

    """
    with op.batch_alter_table("author") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now(timezone.utc)))
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                nullable=False,
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            )
        )

    with op.batch_alter_table("book") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now(timezone.utc)))
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                nullable=False,
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            )
        )

    with op.batch_alter_table("category") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now(timezone.utc)))
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                nullable=False,
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            )
        )

    with op.batch_alter_table("page") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now(timezone.utc)))
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                nullable=False,
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            )
        )

    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now(timezone.utc)))
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                nullable=False,
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            )
        )


def downgrade() -> None:
    """Drop ``created_at`` and ``updated_at`` columns from each affected table.

    Returns:
        None

    """
    with op.batch_alter_table("author") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("category") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("page") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")
