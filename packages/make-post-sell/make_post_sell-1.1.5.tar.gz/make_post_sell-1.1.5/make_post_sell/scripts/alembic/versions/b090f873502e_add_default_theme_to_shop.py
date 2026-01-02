"""add default_theme to shop

Revision ID: b090f873502e
Revises: 16b9fd6d0f70
Create Date: 2025-10-04 14:11:13.516680

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b090f873502e"
down_revision = "16b9fd6d0f70"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add default_theme column to mps_shop table with default 1 (light mode)
    op.add_column(
        "mps_shop",
        sa.Column("default_theme", sa.BigInteger(), nullable=False, server_default="1"),
    )


def downgrade():
    # Remove default_theme column from mps_shop table
    op.drop_column("mps_shop", "default_theme")
