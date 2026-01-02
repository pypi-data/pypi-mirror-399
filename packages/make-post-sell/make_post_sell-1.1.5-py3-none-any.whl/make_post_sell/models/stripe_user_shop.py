import uuid

from sqlalchemy import Column, Unicode

from .meta import Base, RBase, UUIDType, foreign_key

from sqlalchemy.orm import relationship, backref


class StripeUserShop(RBase, Base):
    """
    A user may have zero or many unique stripe_id for each shop it makes purchases on.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)

    # example: "cus_12345678AbCdEF".
    cus_id = Column(Unicode(64), nullable=False)
    active_card_id = Column(Unicode(64), nullable=True)

    user = relationship(
        argument="User", backref=backref("stripe_user", cascade="all, delete-orphan")
    )

    shop = relationship(
        argument="Shop", backref=backref("stripe_shop", cascade="all, delete-orphan")
    )

    def __init__(self, user=None, shop=None):
        self.id = uuid.uuid1()
        self.user = user
        self.shop = shop

    @property
    def stripe_customer(self):
        """Return this object's remote API stripe Customer object."""
        return self.shop.stripe_customer(self.user)

    @property
    def stripe_customer_default_source(self):
        if self.stripe_customer and self.stripe_customer.default_source:
            return self.stripe_customer.sources.retrieve(
                self.stripe_customer.default_source
            )
        return None

    @property
    def stripe_cards(self):
        # Check if Stripe is configured for this shop
        if self.shop.stripe is None:
            return []

        return self.shop.stripe.Customer.list_payment_methods(
            self.stripe_customer, type="card"
        )["data"]

    @property
    def stripe_card_ids(self):
        return [card.id for card in self.stripe_cards]

    def get_card_by_id(self, card_id):
        """return card data by card payment id or None."""
        for card in self.stripe_cards:
            if card.id == card_id:
                return card

    @property
    def active_card(self):
        # If we have an active_card_id, try to get that card
        if self.active_card_id:
            card = self.get_card_by_id(self.active_card_id)
            if card:
                return card

        # If no active card or the active card doesn't exist anymore,
        # automatically set the first available card as active
        available_cards = self.stripe_cards
        if available_cards:
            # Set the first card as active
            self.active_card_id = available_cards[0].id
            # Save to database using object_session
            from sqlalchemy.orm.session import object_session

            session = object_session(self)
            if session:
                session.add(self)
                session.flush()
            return available_cards[0]

        return None


def get_all_stripe_user_shop_objects(dbsession):
    return dbsession.query(StripeUserShop).all()


def get_all_stripe_customer_objects(dbsession):
    """
    Return all Stripe customer objects.
    created timestamp (newest first).
    """
    return [i.stripe_customer for i in dbsession.query(StripeUserShop).all()]
