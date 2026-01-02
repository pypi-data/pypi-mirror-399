import uuid
from sqlalchemy import Column, BigInteger, Unicode, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp


class UserCryptoRefundAddress(RBase, Base):
    """
    Stores cryptocurrency refund addresses for users per shop.
    One user can have one address per shop per coin type.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)

    # Coin type (e.g., 'XMR', 'BTC', 'LTC', 'DOGE', 'BCH')
    coin_type = Column(Unicode(32), nullable=False)

    # The refund address for this coin type
    address = Column(Unicode(256), nullable=False)

    # Optional label/description
    label = Column(Unicode(128), nullable=True)

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    # Relationships
    user = relationship("User", backref="crypto_refund_addresses")
    shop = relationship("Shop", backref="user_crypto_refund_addresses")

    def __init__(self, user, shop, coin_type, address, label=None):
        self.id = uuid.uuid1()
        self.user = user
        self.shop = shop
        self.coin_type = coin_type.upper()
        self.address = address
        self.label = label
        now = now_timestamp()
        self.created_timestamp = now
        self.updated_timestamp = now


# Create unique constraint for user_id + shop_id + coin_type
UniqueConstraint(
    UserCryptoRefundAddress.user_id,
    UserCryptoRefundAddress.shop_id,
    UserCryptoRefundAddress.coin_type,
    name="uq_user_crypto_refund_address_user_shop_coin",
)


def get_user_crypto_refund_address(dbsession, user, shop, coin_type):
    """Get the refund address for a user, shop, and coin type."""
    return (
        dbsession.query(UserCryptoRefundAddress)
        .filter(
            UserCryptoRefundAddress.user_id == user.id,
            UserCryptoRefundAddress.shop_id == shop.id,
            UserCryptoRefundAddress.coin_type == coin_type.upper(),
        )
        .first()
    )
