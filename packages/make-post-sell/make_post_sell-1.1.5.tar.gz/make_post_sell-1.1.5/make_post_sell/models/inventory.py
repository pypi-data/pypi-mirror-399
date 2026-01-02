import uuid
from sqlalchemy import Column, Integer, BigInteger
from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key
from sqlalchemy.orm import relationship


class Inventory(RBase, Base):
    """This class represents the inventory of a product at a specific location."""

    id = Column(UUIDType, primary_key=True, index=True)
    shop_location_id = Column(
        UUIDType, foreign_key("ShopLocation", "id"), nullable=False
    )
    product_id = Column(UUIDType, foreign_key("Product", "id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    shop_location = relationship("ShopLocation", uselist=False)
    product = relationship("Product", uselist=False)

    def __init__(self, shop_location, product, quantity=0):
        if not product.is_physical:
            raise ValueError("Cannot create inventory for a digital product")
        self.id = uuid.uuid1()
        self.shop_location = shop_location
        self.product = product
        self.quantity = quantity
        self.created_timestamp = now_timestamp()
        self.updated_timestamp = now_timestamp()

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.updated_timestamp = now_timestamp()


def get_inventory_by_product_and_shop_location(dbsession, product_id, shop_location_id):
    """
    Query the Inventory table by product_id and shop_location_id.

    :param dbsession: The SQLAlchemy session object.
    :param product_id: The UUID of the product.
    :param shop_location_id: The UUID of the shop location.
    :return: The Inventory object if found, else None.
    """
    return (
        dbsession.query(Inventory)
        .filter_by(product_id=product_id, shop_location_id=shop_location_id)
        .first()
    )
