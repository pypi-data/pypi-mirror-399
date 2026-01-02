"""Add crypto_quote_expiry_seconds to shop

Revision ID: 193438acaa95
Revises: 81d65d8605c2
Create Date: 2025-09-20 21:31:26.257478

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "193438acaa95"
down_revision = "81d65d8605c2"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add crypto quote expiry time column with default of 3600 seconds (60 minutes)
    op.add_column(
        "mps_shop",
        sa.Column(
            "crypto_quote_expiry_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="3600",
        ),
    )


def downgrade():
    op.drop_column("mps_shop", "crypto_quote_expiry_seconds")
