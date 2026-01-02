import uuid

from sqlalchemy import Column, BigInteger, Boolean, Unicode, UnicodeText, func

from sqlalchemy import and_

from .meta import (
    Base,
    RBase,
    UUIDType,
    now_timestamp,
    foreign_key,
    get_object_by_id,
    get_objects_by_ids,
)

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.orm import relationship

from .user_shop import UserShop

from .stripe_user_shop import StripeUserShop

from slugify import slugify

from ..lib.hex_color import color_scale

from ..lib.render import markdown_to_html

try:
    unicode("")
except:
    from six import u as unicode


class Shop(RBase, Base):
    """This class represents a shop."""

    id = Column(UUIDType, primary_key=True, index=True)
    name = Column(Unicode(64), unique=True, nullable=False)
    domain_name = Column(Unicode(256), unique=True)

    # todo: rename to description_raw.
    description = Column(UnicodeText, nullable=True)
    description_html = Column(UnicodeText, nullable=True)

    terms_of_service_raw = Column(UnicodeText, nullable=True)
    terms_of_service_html = Column(UnicodeText, nullable=True)

    privacy_policy_raw = Column(UnicodeText, nullable=True)
    privacy_policy_html = Column(UnicodeText, nullable=True)

    billing_address = Column(UnicodeText, nullable=False)
    phone_number = Column(Unicode(32), nullable=False)

    # The text at the very top of the shop's pages.
    ribbon_text = Column(UnicodeText, nullable=True, default="")
    ribbon_text_color = Column(Unicode(32), nullable=True, default="")
    ribbon_color_1 = Column(Unicode(32), nullable=True, default="")
    ribbon_color_2 = Column(Unicode(32), nullable=True, default="")

    # CSS Grid Lanes (masonry layout) - enabled by default
    grid_lanes_enabled = Column(Boolean, default=True)

    # example: "UA-XX31XX60-3".
    google_analytics_id = Column(Unicode(32), nullable=True, default="")
    plausible_domain_name = Column(Unicode(256), nullable=True, default="")

    # example: "cus_12345678AbCdEF" but may be null.
    # this is how the shop pays for make_post_sell.
    stripe_id = Column(Unicode(32), unique=True, nullable=True)

    # these keys allow make_post_sell to charge
    # cards on behalf of the shop's stripe account.
    # stripe_secret_api_key = Column(Unicode(64), nullable=True)
    # stripe_public_api_key = Column(Unicode(64), nullable=True)
    stripe_secret_api_key = Column(Unicode(128), nullable=True)
    stripe_public_api_key = Column(Unicode(128), nullable=True)
    stripe_enabled = Column(Boolean, default=True)

    # PayPal API credentials for accepting payments
    paypal_client_id = Column(Unicode(128), nullable=True)
    paypal_secret = Column(Unicode(128), nullable=True)
    paypal_enabled = Column(Boolean, default=True)

    # Adyen API credentials for accepting payments
    adyen_api_key = Column(Unicode(128), nullable=True)
    adyen_merchant_account = Column(Unicode(128), nullable=True)
    adyen_client_key = Column(Unicode(128), nullable=True)
    adyen_hmac_key = Column(Unicode(128), nullable=True)
    adyen_enabled = Column(Boolean, default=True)

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    disabled = Column(Boolean, default=False)

    maint_mode = Column(Boolean, default=False)
    favicon = Column(Boolean, default=False)
    logo_banner = Column(Boolean, default=False)

    # Comment/Review system settings
    comments_enabled = Column(Boolean, default=True)
    comments_require_purchase = Column(Boolean, default=False)
    comments_require_approval = Column(Boolean, default=False)

    # Payment risk thresholds (in cents)
    payment_risk_threshold_mid_cents = Column(
        BigInteger, nullable=False, default=1000
    )  # Risk threshold between petty and mid tier (default $10)
    payment_risk_threshold_high_cents = Column(
        BigInteger, nullable=False, default=10000
    )  # Risk threshold between mid and high tier (default $100)

    # Cryptocurrency quote expiry time in seconds
    crypto_quote_expiry_seconds = Column(
        BigInteger, nullable=False, default=3600
    )  # Default 60 minutes

    # Default theme for shop visitors (0=dark, 1=light)
    default_theme = Column(BigInteger, nullable=False, default=1)  # Default light mode

    # many to many uses association_proxy.
    users = association_proxy("shop_users", "user", creator=lambda u: UserShop(user=u))

    carts = relationship(argument="Cart", lazy="dynamic", back_populates="shop")

    # many to many uses association_proxy.
    stripe_users = association_proxy(
        "stripe_users", "user", creator=lambda u: StripeUserShop(user=u)
    )

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    products = relationship(argument="Product", lazy="dynamic", back_populates="shop")

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    coupons = relationship(
        argument="Coupon",
        back_populates="shop",
        lazy="dynamic",
        order_by="desc(Coupon.created_timestamp)",
    )

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    invoices = relationship("Invoice", back_populates="shop", lazy="dynamic")

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    shop_locations = relationship(
        argument="ShopLocation", lazy="dynamic", back_populates="shop"
    )

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    search_requests = relationship(
        argument="ShopSearchRequest", lazy="dynamic", back_populates="shop"
    )

    def __init__(self, name, phone_number, billing_address, description):
        self.id = uuid.uuid1()
        self.name = name
        self.phone_number = phone_number
        self.billing_address = billing_address
        self.description = description
        self.updated_timestamp = now_timestamp()
        self.created_timestamp = now_timestamp()

    def get_usershop_for_user(self, user):
        """Given a User object, return the UserShop object or None."""
        if self.dbsession is not None:
            return (
                self.dbsession.query(UserShop)
                .filter(
                    UserShop.shop == self,
                    UserShop.user == user,
                )
                .one_or_none()
            )

    def add_user_to_shop(self, user, role_id=0):
        """Add User object to UserShop."""
        role_id = int(role_id)
        us = self.get_usershop_for_user(user)
        if us is None:
            us = UserShop(user=user, shop=self, role_id=role_id)
            self.shop_users.append(us)
        else:
            us.role_id = role_id
        return us

    @property
    def owners(self):
        """Returns a list of user objects who have the owner role on this shop."""
        # us is a user_shop object.
        return [us.user for us in self.shop_users if us.is_owner]

    @property
    def editors(self):
        """Returns a list of user objects who have the editor role on this shop."""
        return self.owners + [us.user for us in self.shop_users if us.is_editor]

    @property
    def members(self):
        """Returns a list of user objects who have the member role on this shop."""
        return self.editors + [us.user for us in self.shop_users if us.is_member]

    def is_owner(self, user):
        """Check if the given user is an owner of this shop."""
        if not user:
            return False
        return user in self.owners

    def is_editor(self, user):
        """Check if the given user is an editor of this shop."""
        if not user:
            return False
        return user in self.editors

    def is_member(self, user):
        """Check if the given user is a member of this shop."""
        if not user:
            return False
        return user in self.members

    @property
    def slug(self):
        """return slug from name"""
        return slugify(self.name)

    @property
    def is_stripe_ready(self):
        """Check if shop has Stripe API keys configured."""
        if self.stripe_secret_api_key and self.stripe_public_api_key:
            return True
        return False

    @property
    def is_stripe_not_ready(self):
        return not self.is_stripe_ready

    @property
    def is_paypal_ready(self):
        """Check if shop has PayPal API credentials configured."""
        if self.paypal_client_id and self.paypal_secret:
            return True
        return False

    @property
    def is_paypal_not_ready(self):
        return not self.is_paypal_ready

    @property
    def is_adyen_ready(self):
        """Check if shop has Adyen API credentials configured."""
        if self.adyen_api_key and self.adyen_merchant_account:
            return True
        return False

    @property
    def is_adyen_not_ready(self):
        return not self.is_adyen_ready

    def is_ready_for_payment(self, request):
        """Check if shop is ready based on enabled payment methods."""
        # If Stripe is enabled, shop needs Stripe API keys
        if request.stripe_enabled:
            if self.is_stripe_ready:
                return True

        # If PayPal is enabled, shop needs PayPal API credentials
        if request.paypal_enabled:
            if self.is_paypal_ready:
                return True

        # If Adyen is enabled, shop needs Adyen API credentials
        if getattr(request, "adyen_enabled", False):
            if self.is_adyen_ready:
                return True

        # If Monero is enabled, check if shop has configured processor and RPC is available
        if request.monero_enabled and request.monero_rpc_available:
            from .crypto_processor import CryptoProcessor

            processor = (
                request.dbsession.query(CryptoProcessor)
                .filter(
                    CryptoProcessor.shop_id == self.id,
                    CryptoProcessor.coin_type == "XMR",
                    CryptoProcessor.enabled == True,
                )
                .first()
            )
            if processor:
                return True

        # If Dogecoin is enabled, check if shop has configured processor and RPC is available
        if request.dogecoin_enabled and request.dogecoin_rpc_available:
            from .crypto_processor import CryptoProcessor

            processor = (
                request.dbsession.query(CryptoProcessor)
                .filter(
                    CryptoProcessor.shop_id == self.id,
                    CryptoProcessor.coin_type == "DOGE",
                    CryptoProcessor.enabled == True,
                )
                .first()
            )
            if processor:
                return True

        # No payment methods available or properly configured
        return False

    @property
    def stripe(self):
        """Return a stripe object using this shop's secret api key."""
        if hasattr(self, "_stripe") == False:
            if self.stripe_secret_api_key:
                import stripe

                stripe.api_key = self.stripe_secret_api_key
                self._stripe = stripe
            else:
                self._stripe = None
        return self._stripe

    def stripe_user_shop(self, user):
        """Return the stripe_user_shop object from our database for this user, or None."""
        return (
            self.dbsession.query(StripeUserShop)
            .filter(
                StripeUserShop.user == user,
                StripeUserShop.shop == self,
            )
            .one_or_none()
        )

    def stripe_customer_id(self, user):
        """Return the stripe_customer id from our database for this user, or None."""
        stripe_user_shop = self.stripe_user_shop(user)

        if stripe_user_shop:
            return stripe_user_shop.cus_id

    def stripe_customer(self, user, create=False):
        """
        Return the stripe customer object for this shop for a given user.
        If missing, create one and return, if the `create` parameter is True
        else return None.
        """
        stripe_customer_id = self.stripe_customer_id(user)

        if stripe_customer_id is None:
            if create == False:
                return None

            # create a new stripe customer.
            customer = self.stripe.Customer.create(email=user.email, expand=["sources"])

            # create a new many-to-many user to shop stripe customer.
            stripe_user_shop = StripeUserShop(user, self)
            stripe_user_shop.cus_id = customer.id
            stripe_customer_id = customer.id

            # flush relationship to database.
            self.dbsession.add(stripe_user_shop)
            self.dbsession.flush()
            return customer

        return self.stripe.Customer.retrieve(stripe_customer_id, expand=["sources"])

    def list_stripe_charges(self, stripe_customer=None):
        """
        Return a list of all charges for this shop.
        Optionally pass a stripe Customer object to filter.
        """
        if stripe_customer is not None:
            return self.stripe.Charge.list(customer=stripe_customer)
        return self.stripe.Charge.list()

    @property
    def paypal(self):
        """Return a PayPal SDK API instance using this shop's credentials."""
        if hasattr(self, "_paypal") == False:
            if self.paypal_client_id and self.paypal_secret:
                import paypalrestsdk

                # Get sandbox mode from request/config if available
                # Default to sandbox for safety
                mode = "sandbox"
                if hasattr(self, "dbsession") and self.dbsession:
                    try:
                        from pyramid.threadlocal import get_current_request
                        request = get_current_request()
                        if request and hasattr(request, "app"):
                            sandbox_mode = request.app.get("paypal.sandbox_mode", True)
                            if isinstance(sandbox_mode, str):
                                sandbox_mode = sandbox_mode.strip().lower() in ("1", "true", "yes", "on")
                            if not sandbox_mode:
                                mode = "live"
                    except:
                        pass

                api = paypalrestsdk.Api({
                    'mode': mode,
                    'client_id': self.paypal_client_id,
                    'client_secret': self.paypal_secret
                })
                self._paypal = api
            else:
                self._paypal = None
        return self._paypal

    def paypal_user_shop(self, user):
        """Return the paypal_user_shop object from our database for this user, or None."""
        from .paypal_user_shop import PayPalUserShop

        return (
            self.dbsession.query(PayPalUserShop)
            .filter(
                PayPalUserShop.user == user,
                PayPalUserShop.shop == self,
            )
            .one_or_none()
        )

    @property
    def adyen(self):
        """Return an Adyen SDK instance using this shop's credentials."""
        if hasattr(self, "_adyen") == False:
            if self.adyen_api_key and self.adyen_merchant_account:
                import Adyen

                adyen = Adyen.Adyen()
                adyen.client.xapikey = self.adyen_api_key

                # Get test/live mode from request/config if available
                # Default to test for safety
                platform = "test"
                if hasattr(self, "dbsession") and self.dbsession:
                    try:
                        from pyramid.threadlocal import get_current_request
                        request = get_current_request()
                        if request and hasattr(request, "app"):
                            test_mode = request.app.get("adyen.test_mode", True)
                            if isinstance(test_mode, str):
                                test_mode = test_mode.strip().lower() in ("1", "true", "yes", "on")
                            if not test_mode:
                                platform = "live"
                    except:
                        pass

                adyen.client.platform = platform
                self._adyen = adyen
            else:
                self._adyen = None
        return self._adyen

    @property
    def theme_base_color(self):
        # return the user defined base for shop or default.
        return self.ribbon_color_1 or "#5871ad"

    @property
    def theme_link_color(self):
        return color_scale(self.theme_base_color, 0.75)

    def absolute_url(self, request, slug=True):
        """
        The absolute URI to the shop's page.

        For example:

          https://my.makepostsell.com/s/<shop-uuid>
        """
        if slug:
            return f"{request.host_url}/s/{self.id}/{self.slug}"
        return f"{request.host_url}/s/{self.id}"

    def absolute_settings_url(self, request):
        """
        The absolute URI to the shop's settings page.

        For example:

          https://my.makepostsell.com/s/<shop-uuid>/settings
        """
        return f"{self.absolute_url(request, slug=False)}/settings"

    def absolute_about_url(self, request):
        """
        The absolute URI to the shop's about page.

        For example:

          https://my.makepostsell.com/s/<shop-uuid>/about
        """
        # why ure slug for this URL, is it for SEO?
        return f"{self.absolute_url(request)}/about"

    def absolute_terms_url(self, request):
        return f"{self.absolute_url(request, slug=False)}/terms"

    def absolute_privacy_policy_url(self, request):
        return f"{self.absolute_url(request, slug=False)}/privacy-policy"

    def absolute_sales_url(self, request):
        return f"{self.absolute_url(request, slug=False)}/sales"

    def set_description(self, new_description):
        self.description = new_description
        self.description_html = markdown_to_html(self.description, self)

    @property
    def privacy_policy(self):
        return self.privacy_policy_html

    @privacy_policy.setter
    def privacy_policy(self, new_privacy_policy_raw):
        self.privacy_policy_raw = new_privacy_policy_raw
        self.privacy_policy_html = markdown_to_html(self.privacy_policy_raw, self)

    @property
    def terms_of_service(self):
        return self.terms_of_service_html

    @terms_of_service.setter
    def terms_of_service(self, new_terms_of_service_raw):
        self.terms_of_service_raw = new_terms_of_service_raw
        self.terms_of_service_html = markdown_to_html(self.terms_of_service_raw, self)

    def get_carts_for_user(self, user):
        """return all of this Shop's Cart objects for the given User."""
        from .cart import Cart

        return self.carts.filter(and_(Cart.shop == self, Cart.user == user))

    def make_cart_active_for_user(self, user, cart):
        for c in self.get_carts_for_user(user):
            if cart != c:
                c.active = False
            else:
                c.active = True
            self.dbsession.add(c)
        self.dbsession.flush()

    def get_active_cart_for_user(self, user):
        carts = self.get_carts_for_user(user)
        for cart in carts:
            if cart.active == True:
                return cart

    def create_new_cart_for_user(self, user):
        from .cart import Cart

        cart = Cart()
        cart.user = user
        cart.shop = self
        self.dbsession.add(cart)
        self.dbsession.flush()
        self.make_cart_active_for_user(user, cart)
        return cart

    def stamp_updated_timestamp(self):
        self.updated_timestamp = now_timestamp()


def is_shop_name_available(dbsession, name):
    return not _shop_by_name_query(dbsession, unicode(name)).count()


def is_shop_name_valid(name):
    """Test if shop name meets our criteria for validity."""
    # Choices here are subject to change.
    # allow dashes.
    name = name.replace("-", "")
    # allow period.
    name = name.replace(".", "")
    # allow spaces.
    name = name.replace(" ", "")
    # allow ' single quote.
    name = name.replace("'", "")
    return name.isalnum()


def _shop_by_name_query(dbsession, name):
    """query Shop by case insensitive name."""
    return dbsession.query(Shop).filter(func.lower(Shop.name) == unicode(name.lower()))


def _shop_by_domain_name_query(dbsession, domain_name):
    """query Shop by case insensitive domain name."""
    return dbsession.query(Shop).filter(
        func.lower(Shop.domain_name) == unicode(domain_name.lower())
    )


def get_shop_by_name(dbsession, name):
    """Try to get Shop object by name or return None"""
    if name:
        return _shop_by_name_query(dbsession, name).one_or_none()


def get_shop_by_domain_name(dbsession, domain_name):
    """Try to get Shop object by name or return None"""
    if domain_name:
        return _shop_by_domain_name_query(dbsession, domain_name).one_or_none()


def get_shop_by_id(dbsession, shop_id):
    """Try to get Shop object by id or return None."""
    return get_object_by_id(dbsession, shop_id, Shop)


def get_shops_by_ids(dbsession, shop_ids):
    """Try to get Shop objects by ids or return None."""
    return get_objects_by_ids(dbsession, shop_ids, Shop)
