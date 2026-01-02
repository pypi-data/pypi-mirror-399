"""add adyen payment columns to shop and invoice

Revision ID: 3734955e7379
Revises: 63d935094f97
Create Date: 2025-12-22 16:19:40.557406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3734955e7379'
down_revision = '63d935094f97'
branch_labels = None
depends_on = None


def upgrade():
    # Add Adyen columns to mps_shop
    op.add_column(
        'mps_shop',
        sa.Column('adyen_api_key', sa.Unicode(128), nullable=True)
    )
    op.add_column(
        'mps_shop',
        sa.Column('adyen_merchant_account', sa.Unicode(128), nullable=True)
    )
    op.add_column(
        'mps_shop',
        sa.Column('adyen_client_key', sa.Unicode(128), nullable=True)
    )
    op.add_column(
        'mps_shop',
        sa.Column('adyen_hmac_key', sa.Unicode(128), nullable=True)
    )
    op.add_column(
        'mps_shop',
        sa.Column('adyen_enabled', sa.Boolean(), nullable=False, server_default='1')
    )

    # Add Adyen PSP reference column to mps_invoice
    op.add_column(
        'mps_invoice',
        sa.Column('adyen_psp_reference', sa.Unicode(64), nullable=True)
    )


def downgrade():
    # Remove Invoice column
    op.drop_column('mps_invoice', 'adyen_psp_reference')

    # Remove Shop columns
    op.drop_column('mps_shop', 'adyen_enabled')
    op.drop_column('mps_shop', 'adyen_hmac_key')
    op.drop_column('mps_shop', 'adyen_client_key')
    op.drop_column('mps_shop', 'adyen_merchant_account')
    op.drop_column('mps_shop', 'adyen_api_key')
