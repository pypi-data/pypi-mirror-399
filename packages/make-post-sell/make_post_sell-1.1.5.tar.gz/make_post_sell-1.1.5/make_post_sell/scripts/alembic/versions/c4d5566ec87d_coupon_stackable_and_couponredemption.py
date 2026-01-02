"""Coupon.stackable and CouponRedemption

Revision ID: c4d5566ec87d
Revises: e12bbe39d87e
Create Date: 2021-01-16 11:18:10.302974

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4d5566ec87d"
down_revision = "e12bbe39d87e"
branch_labels = None
depends_on = None

from make_post_sell.models.meta import UUIDType


def upgrade():
    op.create_table(
        "mps_coupon_redemption",
        sa.Column("id", UUIDType, nullable=False),
        sa.Column("coupon_id", UUIDType, nullable=False),
        sa.Column("invoice_id", UUIDType, nullable=False),
        sa.Column("shop_id", UUIDType, nullable=False),
        sa.Column("user_id", UUIDType, nullable=False),
        sa.Column("created_timestamp", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coupon_id"],
            ["mps_coupon.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["mps_invoice.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["mps_shop.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["mps_user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mps_coupon_redemption_id"),
        "mps_coupon_redemption",
        ["id"],
        unique=True,
    )
    op.add_column(
        "mps_coupon",
        sa.Column("stackable", sa.Boolean(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_column("mps_coupon", "stackable")
    op.drop_index(
        op.f("ix_mps_coupon_redemption_id"), table_name="mps_coupon_redemption"
    )
    op.drop_table("mps_coupon_redemption")
