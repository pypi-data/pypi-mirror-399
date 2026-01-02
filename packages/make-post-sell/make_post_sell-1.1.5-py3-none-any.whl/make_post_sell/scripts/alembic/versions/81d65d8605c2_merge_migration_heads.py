"""merge migration heads and add comment settings

Revision ID: 81d65d8605c2
Revises: 1b3ecdde9e65, fd9f7e2f2b78
Create Date: 2025-06-24 08:09:33.656088

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "81d65d8605c2"
down_revision = ("1b3ecdde9e65", "fd9f7e2f2b78")
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    # Add comment columns that may have been missed in the merge
    import sqlalchemy as sa
    from alembic import op
    from sqlalchemy import text

    # Check if columns exist before adding them
    conn = op.get_bind()

    # Check if comments_enabled exists
    try:
        conn.execute(text("SELECT comments_enabled FROM mps_shop LIMIT 1"))
    except:
        op.add_column(
            "mps_shop",
            sa.Column(
                "comments_enabled", sa.Boolean(), nullable=True, server_default="1"
            ),
        )

    # Check if comments_require_purchase exists
    try:
        conn.execute(text("SELECT comments_require_purchase FROM mps_shop LIMIT 1"))
    except:
        op.add_column(
            "mps_shop",
            sa.Column(
                "comments_require_purchase",
                sa.Boolean(),
                nullable=True,
                server_default="0",
            ),
        )

    # Check if comments_require_approval exists
    try:
        conn.execute(text("SELECT comments_require_approval FROM mps_shop LIMIT 1"))
    except:
        op.add_column(
            "mps_shop",
            sa.Column(
                "comments_require_approval",
                sa.Boolean(),
                nullable=True,
                server_default="0",
            ),
        )


def downgrade():
    op.drop_column("mps_shop", "comments_require_approval")
    op.drop_column("mps_shop", "comments_require_purchase")
    op.drop_column("mps_shop", "comments_enabled")
