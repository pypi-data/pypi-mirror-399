"""stripe shop user active card id

Revision ID: b8be6cd51cbd
Revises: 1275752bc491
Create Date: 2022-08-03 11:53:34.191328

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8be6cd51cbd"
down_revision = "1275752bc491"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_stripe_user_shop",
        sa.Column("active_card_id", sa.Unicode(length=64), nullable=True),
    )


def downgrade():
    op.drop_column("mps_stripe_user_shop", "active_card_id")
