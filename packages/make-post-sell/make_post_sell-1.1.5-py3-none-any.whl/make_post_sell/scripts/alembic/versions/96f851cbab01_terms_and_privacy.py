"""terms-and-privacy

Revision ID: 96f851cbab01
Revises: 24662905655f
Create Date: 2020-03-21 18:34:12.244626

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "96f851cbab01"
down_revision = "24662905655f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop",
        sa.Column(
            "privacy_policy_html", sa.UnicodeText(), nullable=True, server_default=""
        ),
    )
    op.add_column(
        "mps_shop",
        sa.Column(
            "privacy_policy_raw", sa.UnicodeText(), nullable=True, server_default=""
        ),
    )
    op.add_column(
        "mps_shop",
        sa.Column(
            "terms_of_service_html", sa.UnicodeText(), nullable=True, server_default=""
        ),
    )
    op.add_column(
        "mps_shop",
        sa.Column(
            "terms_of_service_raw", sa.UnicodeText(), nullable=True, server_default=""
        ),
    )


def downgrade():
    op.drop_column("mps_shop", "terms_of_service_raw")
    op.drop_column("mps_shop", "terms_of_service_html")
    op.drop_column("mps_shop", "privacy_policy_raw")
    op.drop_column("mps_shop", "privacy_policy_html")
