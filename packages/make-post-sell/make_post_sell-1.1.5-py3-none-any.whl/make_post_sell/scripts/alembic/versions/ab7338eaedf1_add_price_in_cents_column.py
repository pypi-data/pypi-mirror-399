"""add price_in_cents_column

Revision ID: ab7338eaedf1
Revises: fd9f7e2f2b78
Create Date: 2019-08-10 11:20:43.838087

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ab7338eaedf1"
down_revision = "fd9f7e2f2b78"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_product",
        sa.Column(
            "price_in_cents", sa.BigInteger(), nullable=False, server_default="3.50"
        ),
    )


def downgrade():
    pass
