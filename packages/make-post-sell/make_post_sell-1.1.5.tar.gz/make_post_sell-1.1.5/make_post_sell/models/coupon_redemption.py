import uuid

from sqlalchemy import Column, BigInteger

from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key

from sqlalchemy.orm import relationship


class CouponRedemption(RBase, Base):
    """This class represents a redemption of a Coupon."""

    # The records in this table should be treated as immutable.
    # Once created we should not modify records in this class.

    id = Column(UUIDType, primary_key=True, index=True, unique=True)
    coupon_id = Column(UUIDType, foreign_key("Coupon", "id"), nullable=False)
    invoice_id = Column(UUIDType, foreign_key("Invoice", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)

    coupon = relationship(argument="Coupon", lazy="joined", uselist=False)
    invoice = relationship(argument="Invoice", lazy="joined", uselist=False)
    shop = relationship(argument="Shop", lazy="joined", uselist=False)
    user = relationship(argument="User", lazy="joined", uselist=False)

    def __init__(self, coupon, invoice, shop, user):
        self.id = uuid.uuid1()
        self.coupon = coupon
        self.invoice = invoice
        self.shop = shop
        self.user = user
        self.created_timestamp = now_timestamp()
