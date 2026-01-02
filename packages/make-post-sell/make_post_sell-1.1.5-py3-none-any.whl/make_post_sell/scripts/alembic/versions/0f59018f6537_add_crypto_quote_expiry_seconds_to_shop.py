"""Add crypto_quote_expiry_seconds to shop

Revision ID: 0f59018f6537
Revises: 193438acaa95
Create Date: 2025-09-21 07:39:30.019212

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0f59018f6537"
down_revision = "193438acaa95"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add payment risk threshold columns
    op.add_column(
        "mps_shop",
        sa.Column(
            "payment_risk_threshold_mid_cents",
            sa.BigInteger(),
            nullable=False,
            server_default="1000",
        ),
    )
    op.add_column(
        "mps_shop",
        sa.Column(
            "payment_risk_threshold_high_cents",
            sa.BigInteger(),
            nullable=False,
            server_default="10000",
        ),
    )


def downgrade():
    op.drop_column("mps_shop", "payment_risk_threshold_high_cents")
    op.drop_column("mps_shop", "payment_risk_threshold_mid_cents")
