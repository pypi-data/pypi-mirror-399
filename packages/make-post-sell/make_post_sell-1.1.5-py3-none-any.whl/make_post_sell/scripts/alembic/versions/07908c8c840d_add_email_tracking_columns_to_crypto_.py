"""add_email_tracking_columns_to_crypto_payment

Revision ID: 07908c8c840d
Revises: 0f59018f6537
Create Date: 2025-09-26 13:35:10.443559

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "07908c8c840d"
down_revision = "0f59018f6537"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add email tracking columns to prevent duplicate emails
    op.add_column(
        "mps_crypto_payment",
        sa.Column("sales_email_sent", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "mps_crypto_payment",
        sa.Column(
            "purchase_email_sent", sa.Boolean(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "mps_crypto_payment",
        sa.Column(
            "refund_email_sent", sa.Boolean(), nullable=False, server_default="0"
        ),
    )


def downgrade():
    # Remove email tracking columns
    op.drop_column("mps_crypto_payment", "refund_email_sent")
    op.drop_column("mps_crypto_payment", "purchase_email_sent")
    op.drop_column("mps_crypto_payment", "sales_email_sent")
