import uuid

from sqlalchemy import Column, BigInteger

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp

from sqlalchemy.orm import relationship, backref


class CartCoupon(RBase, Base):
    """
    Many to many, Carts to Coupons.
    A relationship signifies the application of a coupon to a cart.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    cart_id = Column(UUIDType, foreign_key("Cart", "id"), nullable=False)
    coupon_id = Column(UUIDType, foreign_key("Coupon", "id"), nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)

    cart = relationship(
        argument="Cart", backref=backref("cart_coupons", cascade="all, delete-orphan")
    )

    coupon = relationship(
        argument="Coupon", backref=backref("coupon_carts", cascade="all, delete-orphan")
    )

    def __init__(self, cart=None, coupon=None):
        self.id = uuid.uuid1()
        self.cart = cart
        self.coupon = coupon
        self.created_timestamp = now_timestamp()
