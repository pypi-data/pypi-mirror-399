"""add paypal support

Revision ID: 418933067d81
Revises: a7c3e8f1d2b4
Create Date: 2025-12-22 12:06:14.945882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '418933067d81'
down_revision = 'a7c3e8f1d2b4'
branch_labels = None
depends_on = None


def upgrade():
    # Add PayPal credentials columns to mps_shop table
    op.add_column(
        "mps_shop",
        sa.Column("paypal_client_id", sa.Unicode(128), nullable=True),
    )
    op.add_column(
        "mps_shop",
        sa.Column("paypal_secret", sa.Unicode(128), nullable=True),
    )
    op.add_column(
        "mps_shop",
        sa.Column("paypal_enabled", sa.Boolean(), nullable=False, server_default="1"),
    )
    # Add PayPal payment tracking columns to mps_invoice table
    op.add_column(
        "mps_invoice",
        sa.Column("paypal_order_id", sa.Unicode(64), nullable=True),
    )
    op.add_column(
        "mps_invoice",
        sa.Column("paypal_capture_id", sa.Unicode(64), nullable=True),
    )


def downgrade():
    # Remove PayPal columns from mps_invoice table
    op.drop_column("mps_invoice", "paypal_capture_id")
    op.drop_column("mps_invoice", "paypal_order_id")
    # Remove PayPal columns from mps_shop table
    op.drop_column("mps_shop", "paypal_enabled")
    op.drop_column("mps_shop", "paypal_secret")
    op.drop_column("mps_shop", "paypal_client_id")
