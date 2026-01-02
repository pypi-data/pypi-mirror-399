"""password-attempt-throttling

Revision ID: e6ac162d096f
Revises: c263b4fba9e7
Create Date: 2022-06-09 20:52:58.235423

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6ac162d096f"
down_revision = "c263b4fba9e7"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.add_column(
        "mps_user",
        sa.Column("password_attempts", sa.Integer(), nullable=True, server_default="0"),
    )


def downgrade():
    op.drop_column("mps_user", "password_attempts")
