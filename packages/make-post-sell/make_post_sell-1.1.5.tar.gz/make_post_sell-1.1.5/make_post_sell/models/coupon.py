import uuid

from sqlalchemy import Column, BigInteger, Boolean, Unicode, Enum

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.orm import relationship

from .meta import (
    Base,
    RBase,
    UUIDType,
    now_timestamp,
    foreign_key,
    get_object_by_id,
    COUPON_ACTION_TYPES,
)

from .cart_coupon import CartCoupon

from ..lib.currency import (
    dollars_to_cents,
    cents_to_dollars,
)

from datetime import datetime


def timestamp_to_datetime(timestamp):
    """Accepts a milliseconds timestamp integer and returns a datetime"""
    return datetime.fromtimestamp(timestamp / 1000.0)


def datetime_to_timestamp(dt):
    """returns an integer timestamp in milliseconds"""
    epoch_dt = datetime(1970, 1, 1)
    return (dt - epoch_dt).total_seconds() * 1000


class Coupon(RBase, Base):
    """This class represents a coupon."""

    id = Column(UUIDType, primary_key=True, index=True)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)

    # a code must be unique for a shop, but not unique acrossed all shops.
    code = Column(Unicode(256), nullable=False)

    # the coupon description / display name.
    description = Column(Unicode(256), nullable=False)

    # the type of action that this coupon applies to a cart.
    action_type = Column(Enum(*COUPON_ACTION_TYPES, name="action_type"), nullable=False)
    action_value = Column(BigInteger, nullable=False)

    # The amount of times this code may be used.
    max_redemptions = Column(BigInteger, nullable=True)
    max_redemptions_per_user = Column(BigInteger, nullable=True)

    created_timestamp = Column(BigInteger, nullable=False)

    expired_timestamp = Column(BigInteger, nullable=True)

    # Optional. The minimum cart total needed for this coupon to apply.
    cart_qualifier = Column(BigInteger, nullable=True)

    # stackable means coupon may be combined or stacked with
    # other stackable coupons.
    stackable = Column(Boolean, default=False, nullable=False)

    disabled = Column(Boolean, default=False)

    # lazy='"joined" performs a left join to reduce queries, it's magic.
    # set uselist=False creates one-to-one relationship.
    shop = relationship(argument="Shop", uselist=False, lazy="joined")

    # many to many uses association_proxy.
    carts = association_proxy(
        "coupon_carts", "cart", creator=lambda c: CartCoupon(cart=c)
    )

    # one to many.
    # returns this coupon's redemptions.
    # lazy="dynamic" returns a query object instread of an InstrumentedList.
    # this is ideal when we want to further filter the results.
    redemptions = relationship(
        argument="CouponRedemption", lazy="dynamic", back_populates="coupon"
    )

    def __init__(
        self,
        shop,
        code,
        description,
        action_type,
        action_value,
        max_redemptions=None,
        max_redemptions_per_user=None,
        expiration_date=None,
        cart_qualifier=None,
    ):
        self.id = uuid.uuid1()
        self.shop = shop
        self.created_timestamp = now_timestamp()

        self.code = code
        self.description = description

        self.action_type = action_type
        self.action_value = action_value

        if self.action_type == "dollar-off":
            self.action_value = dollars_to_cents(action_value)
        elif self.action_type == "percent-off" and action_value > 1:
            self.action_value = action_value / 100

        if max_redemptions:
            self.max_redemptions = max_redemptions

        if max_redemptions_per_user:
            self.max_redemptions_per_user = max_redemptions_per_user

        self.cart_qualifier = None
        if cart_qualifier:
            self.cart_qualifier = dollars_to_cents(cart_qualifier)

        self.expired_timestamp = None
        if expiration_date:
            # convert date string into datetime.
            expiration_datetime = datetime.strptime(expiration_date, "%Y-%m-%d")
            # convert datetime into timestamp.
            # adding 86399000 to get the end of day.
            self.expired_timestamp = (
                datetime_to_timestamp(expiration_datetime) + 86399000
            )

    @property
    def expired_datetime(self):
        if self.expired_timestamp:
            return timestamp_to_datetime(self.expired_timestamp)

    @property
    def is_expired(self):
        if self.expired_timestamp is None:
            return False
        return now_timestamp() >= self.expired_timestamp

    @property
    def is_not_expired(self):
        return not self.is_expired

    @property
    def is_not_valid(self):
        return self.disabled or self.is_expired

    @property
    def is_valid(self):
        return not self.is_not_valid

    @property
    def human_discount(self):
        if self.action_type == "percent-off":
            return f"{int(self.action_value * 100)}% off"
        return f"${cents_to_dollars(self.action_value):,.2f} off"

    @property
    def human_max_redemptions(self):
        if self.max_redemptions:
            return f"{self.max_redemptions}"
        return "&#8734;"

    @property
    def human_limit_per_customer(self):
        if self.max_redemptions_per_user:
            return f"Limit {self.max_redemptions_per_user} per customer."
        return ""

    @property
    def human_valid_thru(self):
        if self.expired_timestamp:
            x = self.expired_datetime.strftime("%A, %b %d, %Y")
            return f"Valid thru {x}."
        return ""

    @property
    def human_minimum_cart(self):
        if self.cart_qualifier:
            return f"any ${cents_to_dollars(self.cart_qualifier):,.2f} cart."
        return "any cart."

    def compute_discount(self, cents):
        """
        Given an integer representing total cents of a transaction,
        Return a new integer representing the total cents after applying
        This coupon's discount terms.
        """
        if self.action_type == "dollar-off":
            cents_after_discount = cents - self.action_value
        if self.action_type == "percent-off":
            cents_after_discount = cents - (cents * self.action_value)
        if cents_after_discount < 0:
            # the transaction total may never be negative.
            cents_after_discount = 0
        return cents_after_discount

    @property
    def shop_uuid_str(self):
        return self.id_to_uuid_str(self.shop_id)


def get_coupon_by_id(dbsession, coupon_id):
    """Try to get Coupon object by id or return None."""
    return get_object_by_id(dbsession, coupon_id, Coupon)


def get_coupons_by_code(dbsession, code, shop=None):
    """
    Given a coupon code and optional shop, return a list of Coupon objects.
    Remember a coupon code may not be unique across all shops.
    """
    if shop is not None:
        return shop.coupons.filter(Coupon.code == code).all()
    return dbsession.query(Coupon).filter(Coupon.code == code).all()
