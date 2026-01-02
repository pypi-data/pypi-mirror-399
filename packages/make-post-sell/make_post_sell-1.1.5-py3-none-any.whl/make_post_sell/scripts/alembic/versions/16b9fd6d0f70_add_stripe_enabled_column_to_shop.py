"""add stripe_enabled column to shop

Revision ID: 16b9fd6d0f70
Revises: 0915b3ff883d
Create Date: 2025-10-04 10:29:05.739831

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16b9fd6d0f70"
down_revision = "0915b3ff883d"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add stripe_enabled column to mps_shop table with default True
    op.add_column(
        "mps_shop",
        sa.Column("stripe_enabled", sa.Boolean(), nullable=False, server_default="1"),
    )


def downgrade():
    # Remove stripe_enabled column from mps_shop table
    op.drop_column("mps_shop", "stripe_enabled")
