"""new ux columns

Revision ID: c263b4fba9e7
Revises: cdad5c220c39
Create Date: 2022-01-31 15:45:34.314442

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c263b4fba9e7"
down_revision = "cdad5c220c39"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_shop",
        sa.Column("maint_mode", sa.Boolean(), nullable=True, server_default="0"),
    )
    op.add_column(
        "mps_shop",
        sa.Column("favicon", sa.Boolean(), nullable=True, server_default="0"),
    )
    op.add_column(
        "mps_user",
        sa.Column("theme_id", sa.BigInteger(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_column("mps_shop", "maint_mode")
    op.drop_column("mps_shop", "favicon")
    op.drop_column("mps_user", "theme_id")
