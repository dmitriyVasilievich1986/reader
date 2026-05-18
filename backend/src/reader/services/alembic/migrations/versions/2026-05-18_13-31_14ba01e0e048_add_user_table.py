"""Alembic migration: add the ``user`` table for application accounts.

Revision ID: 14ba01e0e048
Revises: 8e3f5d72efaf
Create Date: 2026-05-18 13:31:32.493557

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "14ba01e0e048"
down_revision: Union[str, None] = "8e3f5d72efaf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the ``user`` table with auth, profile, and access flags.

    Returns:
        None.

    """
    op.create_table(
        "user",
        sa.Column("id", sa.Integer),
        sa.Column("username", sa.String(150), nullable=False, unique=True),
        sa.Column("email", sa.String(150), nullable=False, unique=True),
        sa.Column("password", sa.String(150), nullable=False),
        sa.Column("first_name", sa.String(150), nullable=True),
        sa.Column("last_name", sa.String(150), nullable=True),
        sa.Column("photo_url", sa.String(255), nullable=True),
        sa.Column("is_admin", sa.Boolean, nullable=False, default=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.PrimaryKeyConstraint("id", name="pk_user"),
        sa.UniqueConstraint("username", name="uq_user_username"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )


def downgrade() -> None:
    """Drop the ``user`` table.

    Returns:
        None.

    """
    op.drop_table("user")
