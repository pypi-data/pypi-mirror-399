"""google_analytics_id

Revision ID: 3e1e70bfe89d
Revises: eadd0d69e133
Create Date: 2019-11-20 11:06:28.092483

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e1e70bfe89d"
down_revision = "eadd0d69e133"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop",
        sa.Column("google_analytics_id", sa.Unicode(length=32), nullable=True),
    )


def downgrade():
    op.drop_column("mps_shop", "google_analytics_id")
