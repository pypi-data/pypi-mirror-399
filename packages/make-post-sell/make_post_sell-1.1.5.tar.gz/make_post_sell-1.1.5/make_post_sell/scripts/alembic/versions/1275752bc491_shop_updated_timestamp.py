"""shop updated timestamp

Revision ID: 1275752bc491
Revises: 201924e6306f
Create Date: 2022-07-27 14:50:19.889862

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1275752bc491"
down_revision = "201924e6306f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop",
        sa.Column(
            "updated_timestamp",
            sa.BigInteger(),
            nullable=False,
            server_default="1657814552131",
        ),
    )


def downgrade():
    op.drop_column("mps_shop", "updated_timestamp")
