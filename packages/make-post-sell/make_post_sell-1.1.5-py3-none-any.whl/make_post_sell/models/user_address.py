import uuid

from sqlalchemy import Column, BigInteger, UnicodeText

from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key, get_object_by_id

from sqlalchemy.orm import relationship


class UserAddress(RBase, Base):
    """This class represents a physical mail address."""

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=True)
    data = Column(UnicodeText)

    created_timestamp = Column(BigInteger, nullable=False)

    user = relationship(argument="User", uselist=False, lazy="joined")

    def __init__(self, data):
        self.created_timestamp = now_timestamp()
        self.id = uuid.uuid1()
        self.data = data


def get_user_address_by_id(dbsession, user_address_id):
    """Try to get UserAddress object by id or return None."""
    return get_object_by_id(dbsession, user_address_id, UserAddress)
