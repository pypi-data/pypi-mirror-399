"""create new active_shop_id column on user table.

Revision ID: 24662905655f
Revises: 3e1e70bfe89d
Create Date: 2020-02-03 00:03:11.599838

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "24662905655f"
down_revision = "3e1e70bfe89d"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column("mps_user", sa.Column("active_shop_id", UUIDType, nullable=True))


def downgrade():
    op.drop_column("mps_user", "active_shop_id")
