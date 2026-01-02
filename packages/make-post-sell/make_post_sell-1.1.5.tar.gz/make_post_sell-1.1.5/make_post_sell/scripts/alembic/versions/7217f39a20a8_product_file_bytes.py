"""product file bytes

Revision ID: 7217f39a20a8
Revises: d38d649cb682
Create Date: 2022-09-13 14:57:57.100700

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7217f39a20a8"
down_revision = "d38d649cb682"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_product",
        sa.Column(
            "json_file_bytes", sa.UnicodeText(), nullable=True, server_default="{}"
        ),
    )
    op.add_column(
        "mps_product",
        sa.Column(
            "total_file_bytes", sa.BigInteger(), nullable=False, server_default="0"
        ),
    )


def downgrade():
    op.drop_column("mps_product", "total_file_bytes")
    op.drop_column("mps_product", "json_file_bytes")
