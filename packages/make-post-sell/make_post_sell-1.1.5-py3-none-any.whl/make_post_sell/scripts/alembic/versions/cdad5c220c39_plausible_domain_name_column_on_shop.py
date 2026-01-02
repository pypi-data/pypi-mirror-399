"""plausible_domain_name column on shop

Revision ID: cdad5c220c39
Revises: bfc4195a7f56
Create Date: 2022-01-07 19:57:52.202252

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cdad5c220c39"
down_revision = "bfc4195a7f56"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mps_shop",
        sa.Column(
            "plausible_domain_name",
            sa.Unicode(length=256),
            nullable=True,
            server_default="",
        ),
    )


def downgrade():
    op.drop_column("mps_shop", "plausible_domain_name")
