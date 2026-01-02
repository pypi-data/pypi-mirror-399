"""product visibility column


Revision ID: 4d9da43b0e86
Revises: af28cc35ed6f
Create Date: 2021-10-27 09:00:32.238571

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d9da43b0e86"
down_revision = "af28cc35ed6f"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_product",
        sa.Column("visibility", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_column("mps_product", "visibility")
