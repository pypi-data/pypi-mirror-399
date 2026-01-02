"""Add swept_confirmations to track sweep transaction confirmations

Revision ID: 0915b3ff883d
Revises: 07908c8c840d
Create Date: 2025-10-02 19:00:08.788508

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0915b3ff883d"
down_revision = "07908c8c840d"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add swept_confirmations column to mps_crypto_payment table
    op.add_column(
        "mps_crypto_payment",
        sa.Column(
            "swept_confirmations", sa.Integer(), nullable=False, server_default="10"
        ),
    )


def downgrade():
    # Remove swept_confirmations column from mps_crypto_payment table
    op.drop_column("mps_crypto_payment", "swept_confirmations")
