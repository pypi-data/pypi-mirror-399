import uuid

from sqlalchemy import Column, BigInteger, Unicode

from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key, get_object_by_id

from sqlalchemy.orm import relationship


class ShopSearchRequest(RBase, Base):
    """This class represents a shop search request result and hits count."""

    id = Column(UUIDType, primary_key=True, index=True)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"))
    user_id = Column(UUIDType, foreign_key("User", "id"))
    keywords = Column(Unicode(128), nullable=False)
    hit_count = Column(BigInteger, nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)

    user = relationship(argument="User", lazy="joined", uselist=False)
    shop = relationship(argument="Shop", lazy="joined", uselist=False)

    def __init__(self, keywords, hit_count, shop=None, user=None):
        self.id = uuid.uuid1()
        # truncate to 128 chars to fit in VarChar.
        self.keywords = keywords[:128]
        self.hit_count = hit_count
        self.shop = shop
        self.user = user
        self.created_timestamp = now_timestamp()


def get_shop_search_request_by_id(dbsession, _id):
    """Try to get ShopSearchRequest object by id or return None."""
    return get_object_by_id(dbsession, _id, ShopSearchRequest)
