import uuid

from sqlalchemy import Column, Integer, BigInteger

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp

from sqlalchemy.orm import relationship, backref

role_id_to_name = {
    0: "owner",  # root.
    1: "editor",  # virtual assistant.
    2: "member",  # viewer.
}


class UserShop(RBase, Base):
    """
    Many shops to many users.
    A relationship signifies the ability to edit a shop and it's products.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    created_timestamp = Column(BigInteger, nullable=False)
    role_id = Column(Integer, nullable=False, default=0)

    user = relationship(
        argument="User", backref=backref("user_shops", cascade="all, delete-orphan")
    )

    shop = relationship(
        argument="Shop", backref=backref("shop_users", cascade="all, delete-orphan")
    )

    def __init__(self, user=None, shop=None, role_id=0):
        self.id = uuid.uuid1()
        self.user = user
        self.shop = shop
        self.role_id = role_id
        self.created_timestamp = now_timestamp()

    def role_name(self):
        return role_id_to_name[self.role_id]

    @property
    def is_owner(self):
        return self.role_id == 0

    @property
    def is_editor(self):
        return self.role_id == 1

    @property
    def is_member(self):
        return self.role_id == 2
