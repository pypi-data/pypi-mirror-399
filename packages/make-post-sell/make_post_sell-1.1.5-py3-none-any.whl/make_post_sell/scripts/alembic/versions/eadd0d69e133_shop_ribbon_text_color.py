"""shop ribbon text color

Revision ID: eadd0d69e133
Revises: 5c40dfb56179
Create Date: 2019-10-29 12:14:10.391983

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eadd0d69e133"
down_revision = "5c40dfb56179"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop", sa.Column("ribbon_text_color", sa.Unicode(length=32), nullable=True)
    )


def downgrade():
    op.drop_column("mps_shop", "ribbon_text_color")
