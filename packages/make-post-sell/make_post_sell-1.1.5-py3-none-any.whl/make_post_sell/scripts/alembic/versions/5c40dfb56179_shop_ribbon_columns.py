"""shop ribbon columns

Revision ID: 5c40dfb56179
Revises: f882f2255cd1
Create Date: 2019-10-29 11:59:01.050032

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c40dfb56179"
down_revision = "f882f2255cd1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop", sa.Column("ribbon_color_1", sa.Unicode(length=32), nullable=True)
    )
    op.add_column(
        "mps_shop", sa.Column("ribbon_color_2", sa.Unicode(length=32), nullable=True)
    )
    op.add_column("mps_shop", sa.Column("ribbon_text", sa.UnicodeText(), nullable=True))


def downgrade():
    op.drop_column("mps_shop", "ribbon_text")
    op.drop_column("mps_shop", "ribbon_color_2")
    op.drop_column("mps_shop", "ribbon_color_1")
