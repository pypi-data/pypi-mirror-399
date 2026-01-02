import uuid

from sqlalchemy import Column, BigInteger

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp

from sqlalchemy.orm import relationship, backref


class UserProduct(RBase, Base):
    """
    Many users to many products.
    A relationship signifies the ability to _download_ a product.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    product_id = Column(UUIDType, foreign_key("Product", "id"), nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)

    user = relationship(
        argument="User",
        backref=backref("user_products", cascade="all, delete-orphan"),
    )

    product = relationship(
        argument="Product",
        backref=backref("product_users", cascade="all, delete-orphan"),
        order_by="UserProduct.created_timestamp",
    )

    def __init__(self, user=None, product=None):
        self.id = uuid.uuid1()
        self.user = user
        self.product = product
        self.created_timestamp = now_timestamp()
