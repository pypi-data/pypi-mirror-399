import uuid

import bcrypt

from sqlalchemy import Column, BigInteger, Integer, Boolean, Unicode, func

from .meta import Base, RBase, UUIDType, now_timestamp, foreign_key, get_object_by_id

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.orm import relationship

from .user_shop import UserShop

from .stripe_user_shop import StripeUserShop

from .user_product import UserProduct

from .user_address import UserAddress, get_user_address_by_id

from .shop import Shop

from .cart import Cart

from .cart import get_cart_by_id

import logging

log = logging.getLogger(__name__)


try:
    unicode("")
except:
    from six import u as unicode


def generate_password(size=32):
    """Return a system generated password"""
    from random import choice

    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    pool = letters + digits
    return "".join([choice(pool) for i in range(size)])


class User(RBase, Base):
    """This class represents a user account."""

    # was this User object authenticated?
    authenticated = False

    id = Column(UUIDType, primary_key=True, index=True)

    active_shop_id = Column(UUIDType, default=None)
    name = Column(Unicode(64), unique=True, nullable=False)
    full_name = Column(Unicode(64))
    email = Column(Unicode(64), unique=True, nullable=False)
    # email_unverified = Column(Unicode(64))
    password = Column(Unicode(64))
    password_attempts = Column(Integer, default=0)
    password_timestamp = Column(BigInteger)
    created_timestamp = Column(BigInteger, nullable=False)
    gravatar = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)

    # TODO: remove this column.
    active_cart_id = Column(UUIDType, nullable=False)
    # TODO: remove this column.
    active_cart_count = Column(Integer, default=0, nullable=False)
    # TODO: remove this column.
    active_cart_total_in_cents = Column(BigInteger, default=0, nullable=False)

    active_address_id = Column(UUIDType, nullable=True)

    # 0 is dark, 1 is light, could have more themes when h@ckz0rs unite.
    theme_id = Column(BigInteger, nullable=False, default=1)

    # many to many uses association_proxy.
    shops = association_proxy("user_shops", "shop", creator=lambda s: UserShop(shop=s))

    # many to many uses association_proxy.
    stripe_shops = association_proxy(
        "stripe_shops", "shop", creator=lambda s: StripeUserShop(shop=s)
    )

    # many to many uses association_proxy.
    # returns all the products that a user has purchased.
    """
    _products = relationship(UserProduct, order_by=[UserProduct.created_timestamp.desc()])
    products = association_proxy(
        "_products", "product", creator=lambda p: UserProduct(product=p)
    )
    """
    products = association_proxy(
        "user_products", "product", creator=lambda p: UserProduct(product=p)
    )

    # one to many.
    # returns this user's carts.
    # lazy="dynamic" returns a query object instread of an InstrumentedList.
    # this is ideal when we want to further filter the results.
    carts = relationship(argument="Cart", lazy="dynamic", back_populates="user")

    addresses = relationship(
        argument="UserAddress", lazy="dynamic", back_populates="user"
    )

    invoices = relationship(argument="Invoice", lazy="dynamic", back_populates="user")

    def __init__(self, email):
        self.name = unicode(f"user-{generate_password(size=8)}")
        self.created_timestamp = now_timestamp()
        self.id = uuid.uuid1()
        self.email = unicode(email)

        # TODO: remove this column.
        self.active_cart_id = uuid.uuid1()

        self.new_password()
        # don't password throttle new User objects.
        self.password_timestamp = 0

    def _generate_raw_password(self):
        """Return a system generated password"""
        # return generate_password(size)
        from random import choice

        numbers = "0123456789"
        return "".join([choice(numbers) for i in range(0, 6)])

    def new_password(self):
        """Generate and return raw password, store password hash into DB."""
        raw_password = self._generate_raw_password()

        # bcrypt works with bytes so we encode to utf-8.
        self.password = bcrypt.hashpw(
            raw_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        self.password_timestamp = now_timestamp()
        self.password_attempts = 0
        return raw_password

    def check_password(self, password):
        """Accept plain-text raw password, create hash, compare with DB."""
        stored_hash = self.password

        # increment password attempts.
        self.password_attempts += 1

        # expire password after 15 minutes.
        # 900000 milliseconds == 15 minutes
        if self.password_timestamp_delta >= 900000:
            return False

        # prevent brute force, allow 10 invalid verification code attempts.
        if self.password_attempts >= 10:
            return False

        # bcrypt works with bytes so we encode to utf-8.
        new_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        ).decode("utf-8")

        log.info(f"new_hash={new_hash} stored_hash={stored_hash}")

        if new_hash == stored_hash:
            return True
        return False

    def throttle_password(self, needed_delta=90000):
        """Return True when throttled, else False"""
        if self.password_timestamp_delta <= needed_delta:
            return True
        return False

    @property
    def password_timestamp_delta(self):
        return now_timestamp() - self.password_timestamp

    def set_active_shop(self, shop):
        self.active_shop_id = shop.id
        self.dbsession.add(self)
        self.dbsession.flush()

    @property
    def active_shop(self):
        """Return the user's active shop, or None."""
        if self.active_shop_id:
            return (
                self.dbsession.query(Shop)
                .filter(Shop.id == self.active_shop_id)
                .one_or_none()
            )

        elif self.shops:
            # if a user doesn't have an active shop but it has
            # at least one shop, set them an active shop.
            shop = self.shops[0]
            self.set_active_shop(shop)
            return shop

    def can_edit_product(self, product):
        """Return True or False"""
        if product and self in product.shop.editors:
            return True
        return False

    def can_not_edit_product(self, product):
        """Return True or False"""
        return not self.can_edit_product(product)

    def can_download_product(self, product):
        """Return True or False"""
        if product:
            if self.can_edit_product(product) or self in product.users:
                return True
            for bundle in product.bundles_with_this_product:
                if self in bundle.users:
                    return True
        return False

    def can_not_download_product(self, product):
        """Return True or False"""
        return not self.can_download_product(product)

    def can_edit_shop(self, shop):
        if shop and self in shop.editors:
            return True
        return False

    def can_not_edit_shop(self, shop):
        return not self.can_edit_shop(shop)

    def owns_cart(self, cart):
        return self == cart.user

    def does_not_own_cart(self, cart):
        return not self.owns_cart(cart)

    def new_address(self, new_address):
        user_address = UserAddress(new_address)
        user_address.user = self
        self.active_address_id = user_address.uuid_str
        return user_address

    @property
    def active_address(self):
        for address in self.addresses:
            if address.id == self.active_address_id:
                return address


def _user_by_name_query(dbsession, name):
    """query User by case insensitive name."""
    return dbsession.query(User).filter(func.lower(User.name) == unicode(name.lower()))


def is_user_name_available(dbsession, name):
    return not _user_by_name_query(dbsession, unicode(name)).count()


def generate_user_name(dbsession, desired_name=""):
    size = 8
    sep = ""
    if desired_name:
        size = 3
        sep = "-"
    name = sep.join([desired_name, generate_password(size)])
    while is_user_name_available(dbsession, name) == False:
        name = sep.join([desired_name, generate_password(size)])
    return name


def is_user_name_valid(name):
    """Test if user name meets our criteria for validity."""
    # Choices here are subject to change.
    # allow dashes.
    name = name.replace("-", "")
    # allow period.
    name = name.replace(".", "")
    # allow spaces.
    name = name.replace(" ", "")
    return name.isalnum()


def get_user_by_name(dbsession, name):
    """Try to get User object by name or return None"""
    if name:
        return _user_by_name_query(dbsession, name).one_or_none()


def get_user_by_id(dbsession, user_id):
    """Try to get User object by id or return None."""
    return get_object_by_id(dbsession, user_id, User)


def get_user_by_email(dbsession, email):
    """Try to get User object by email or return None"""
    if email:
        return dbsession.query(User).filter(User.email == unicode(email)).one_or_none()


def get_or_create_user_by_email(dbsession, email):
    """Try to get User object by email or return new User"""
    lower_email = email.lower()
    user = get_user_by_email(dbsession, email)
    if user is None:
        # create new User for unverified user.
        user = User(email)
        if not is_user_name_available(dbsession, user.name):
            user.name = generate_user_name(dbsession)

    return user
