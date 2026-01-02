"""add grid_lanes_enabled to shop

Revision ID: a7c3e8f1d2b4
Revises: b090f873502e
Create Date: 2025-12-19 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a7c3e8f1d2b4"
down_revision = "b090f873502e"
branch_labels = None
depends_on = None


def upgrade():
    # Add grid_lanes_enabled column to mps_shop table with default True (enabled)
    op.add_column(
        "mps_shop",
        sa.Column("grid_lanes_enabled", sa.Boolean(), nullable=False, server_default="1"),
    )


def downgrade():
    # Remove grid_lanes_enabled column from mps_shop table
    op.drop_column("mps_shop", "grid_lanes_enabled")
