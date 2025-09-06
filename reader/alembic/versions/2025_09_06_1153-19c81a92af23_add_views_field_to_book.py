"""Add views field to book

Revision ID: 19c81a92af23
Revises: 8e3f5d72efaf
Create Date: 2025-09-06 11:53:18.635173

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "19c81a92af23"
down_revision: str | None = "8e3f5d72efaf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "book", sa.Column("views", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("book", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("book", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE book SET created_at = CURRENT_TIMESTAMP")
    op.execute("UPDATE book SET updated_at = CURRENT_TIMESTAMP")

    with op.batch_alter_table("book", schema=None) as batch_op:
        batch_op.alter_column("created_at", nullable=False)
        batch_op.alter_column("updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("book", "views")
    op.drop_column("book", "created_at")
    op.drop_column("book", "updated_at")
