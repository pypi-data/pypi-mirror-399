import uuid
from sqlalchemy import Column, BigInteger, Unicode, Boolean, Index, UniqueConstraint
from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key


class CryptoProcessor(RBase, Base):
    """Configuration for cryptocurrency payment processing per shop."""

    id = Column(UUIDType, primary_key=True, index=True)

    # Shop this processor belongs to
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False, index=True)

    # Cryptocurrency type (XMR, DOGE, BTC, LTC, etc)
    coin_type = Column(Unicode(32), nullable=False, index=True)

    # Is this processor active?
    enabled = Column(Boolean, default=True, nullable=False)

    # Remote cold wallet address to sweep funds to
    sweep_to_address = Column(Unicode(256), nullable=False)

    # Wallet identifier - account index for Monero, label for Bitcoin-like
    wallet_label = Column(Unicode(128), nullable=False)

    # Generic semaphore for bounded scanning across different coin types
    # Format: "type:value" where type is height|blockhash|timestamp
    # XMR: "height:3507980"
    # DOGE/BTC/LTC/BCH: "blockhash:00000000000001a2b3c4d5e6f7..."
    last_scan_semaphore = Column(Unicode(255), nullable=True)

    # Timestamps
    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    def __init__(self, shop_id, coin_type, sweep_to_address):
        self.id = uuid.uuid1()
        self.shop_id = shop_id
        self.coin_type = coin_type.upper()
        self.sweep_to_address = sweep_to_address
        self.created_timestamp = now_timestamp()
        self.updated_timestamp = now_timestamp()


# Create indexes and constraints
Index(
    "ix_crypto_processor_shop_coin", CryptoProcessor.shop_id, CryptoProcessor.coin_type
)
UniqueConstraint(
    CryptoProcessor.shop_id,
    CryptoProcessor.coin_type,
    name="uq_crypto_processor_shop_coin",
)
UniqueConstraint(CryptoProcessor.wallet_label, name="uq_crypto_processor_wallet_label")
