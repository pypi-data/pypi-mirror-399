import uuid
from sqlalchemy import Column, Unicode, BigInteger, Boolean
from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key, get_object_by_id
from sqlalchemy.orm import relationship
from ..lib.currency import cents_to_dollars, dollars_to_cents


class ShopLocation(RBase, Base):
    """This class represents a physical location of a shop."""

    id = Column(UUIDType, primary_key=True, index=True)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    name = Column(Unicode(64), nullable=False)
    address = Column(Unicode(256), nullable=False)
    city = Column(Unicode(64), nullable=False)
    state = Column(Unicode(64), nullable=False)
    country = Column(Unicode(64), nullable=False)
    postal_code = Column(Unicode(16), nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)

    # Delivery options
    local_pickup = Column(Boolean, default=False, nullable=False)
    local_delivery = Column(Boolean, default=False, nullable=False)
    local_shipping = Column(Boolean, default=False, nullable=False)
    international_shipping = Column(Boolean, default=False, nullable=False)

    # Delivery rates in cents
    local_delivery_rate_in_cents = Column(BigInteger, nullable=True)
    local_shipping_rate_in_cents = Column(BigInteger, nullable=True)
    international_shipping_rate_in_cents = Column(BigInteger, nullable=True)

    # Operating hours
    days_open = Column(Unicode(64), nullable=True)  # e.g., "Mon-Fri"
    hours_open = Column(Unicode(64), nullable=True)  # e.g., "9am-5pm"

    shop = relationship("Shop", uselist=False)

    def __init__(self, shop, name, address, city, state, country, postal_code):
        self.id = uuid.uuid1()
        self.shop = shop
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.created_timestamp = now_timestamp()

    @property
    def local_delivery_rate(self):
        return (
            cents_to_dollars(self.local_delivery_rate_in_cents)
            if self.local_delivery_rate_in_cents
            else None
        )

    @local_delivery_rate.setter
    def local_delivery_rate(self, value):
        self.local_delivery_rate_in_cents = dollars_to_cents(value)

    @property
    def local_shipping_rate(self):
        return (
            cents_to_dollars(self.local_shipping_rate_in_cents)
            if self.local_shipping_rate_in_cents
            else None
        )

    @local_shipping_rate.setter
    def local_shipping_rate(self, value):
        self.local_shipping_rate_in_cents = dollars_to_cents(value)

    @property
    def international_shipping_rate(self):
        return (
            cents_to_dollars(self.international_shipping_rate_in_cents)
            if self.international_shipping_rate_in_cents
            else None
        )

    @international_shipping_rate.setter
    def international_shipping_rate(self, value):
        self.international_shipping_rate_in_cents = dollars_to_cents(value)


def get_shop_location_by_id(dbsession, shop_location_id):
    """Try to get ShopLocation object by id or return None."""
    return get_object_by_id(dbsession, shop_location_id, ShopLocation)
