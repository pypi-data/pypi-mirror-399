import uuid

from sqlalchemy import Column, Unicode

from .meta import Base, RBase, UUIDType, foreign_key

from sqlalchemy.orm import relationship, backref


class PayPalUserShop(RBase, Base):
    """
    A user may have zero or many unique PayPal payer IDs for each shop it makes purchases on.
    This tracks saved PayPal payment methods and customer relationships per shop.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)

    # PayPal payer ID (e.g., "PAYERID123ABC")
    payer_id = Column(Unicode(64), nullable=True)

    # Billing agreement ID for reference transactions (optional)
    billing_agreement_id = Column(Unicode(64), nullable=True)

    # Active payment token for saved payment methods (optional)
    active_payment_token = Column(Unicode(128), nullable=True)

    user = relationship(
        argument="User", backref=backref("paypal_user", cascade="all, delete-orphan")
    )

    shop = relationship(
        argument="Shop", backref=backref("paypal_shop", cascade="all, delete-orphan")
    )

    def __init__(self, user=None, shop=None):
        self.id = uuid.uuid1()
        self.user = user
        self.shop = shop

    @property
    def has_billing_agreement(self):
        """Check if this user has an active billing agreement with PayPal."""
        return self.billing_agreement_id is not None

    @property
    def has_saved_payment_method(self):
        """Check if this user has a saved payment token."""
        return self.active_payment_token is not None


def get_all_paypal_user_shop_objects(dbsession):
    """Return all PayPalUserShop objects."""
    return dbsession.query(PayPalUserShop).all()
