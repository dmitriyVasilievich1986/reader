"""Add ``watches_count`` column to the ``book`` table.

Stores a non-null integer count of watches per book, defaulting to zero.

Revision ID: b922d12d33b3
Revises: ca414c66f0fa
Create Date: 2026-05-18 22:13:40.418297

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b922d12d33b3"
down_revision: Union[str, None] = "ca414c66f0fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add non-null ``watches_count`` column with default zero.

    Returns:
        None

    """
    with op.batch_alter_table("book") as batch_op:
        batch_op.add_column(sa.Column("watches_count", sa.Integer, nullable=False, default=0))


def downgrade() -> None:
    """Drop ``watches_count`` from ``book``.

    Returns:
        None

    """
    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_column("watches_count")
