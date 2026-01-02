"""product.is_sellable coluumn

Revision ID: bfc4195a7f56
Revises: 4d9da43b0e86
Create Date: 2021-12-02 17:32:08.498999

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bfc4195a7f56"
down_revision = "4d9da43b0e86"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_product",
        sa.Column("is_sellable", sa.Boolean(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_column("mps_product", "is_sellable")
