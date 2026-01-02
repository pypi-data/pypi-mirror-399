"""add stripe payment tracking columns to invoice

Revision ID: 63d935094f97
Revises: 418933067d81
Create Date: 2025-12-22 15:54:08.424454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d935094f97'
down_revision = '418933067d81'
branch_labels = None
depends_on = None


def upgrade():
    # Add Stripe payment tracking columns to mps_invoice
    op.add_column(
        'mps_invoice',
        sa.Column('stripe_payment_intent_id', sa.Unicode(64), nullable=True)
    )
    op.add_column(
        'mps_invoice',
        sa.Column('stripe_charge_id', sa.Unicode(64), nullable=True)
    )


def downgrade():
    op.drop_column('mps_invoice', 'stripe_charge_id')
    op.drop_column('mps_invoice', 'stripe_payment_intent_id')
