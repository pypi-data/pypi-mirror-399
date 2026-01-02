import uuid

from sqlalchemy import Column, BigInteger

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp

from sqlalchemy.orm import relationship

from ..lib.currency import cents_to_dollars


class Price(RBase, Base):
    """This class tracks a product's price history."""

    id = Column(UUIDType, primary_key=True, index=True)
    product_id = Column(UUIDType, foreign_key("Product", "id"), nullable=False)
    price_in_cents = Column(BigInteger, nullable=False)

    created_timestamp = Column(BigInteger, nullable=False)

    product = relationship(argument="Product", uselist=False, lazy="joined")

    def __init__(self, product, price_in_cents):
        self.id = uuid.uuid1()
        self.product = product
        self.price_in_cents = price_in_cents
        self.created_timestamp = now_timestamp()

    @property
    def price(self):
        return cents_to_dollars(self.price_in_cents)
