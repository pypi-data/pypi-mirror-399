import uuid

import json

from sqlalchemy.orm import relationship

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy import Column, Boolean, BigInteger, Unicode, UnicodeText

from .meta import (
    Base,
    RBase,
    UUIDType,
    foreign_key,
    now_timestamp,
    get_object_by_id,
    bucket_objects_by_id,
)

from .product import get_products_by_ids
from .shop import get_shops_by_ids

from .cart_coupon import CartCoupon

from .inventory import get_inventory_by_product_and_shop_location

from make_post_sell.lib.currency import cents_to_dollars
from make_post_sell.lib.time_funcs import timestamp_to_datetime, timestamp_to_ago_string

try:
    unicode("")
except:
    from six import u as unicode


class Cart(RBase, Base):
    """This class tracks a User's shopping carts."""

    id = Column(UUIDType, primary_key=True, index=True)
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=True)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=True)
    name = Column(Unicode(64))
    public = Column(Boolean, default=False)
    json_cart = Column(UnicodeText, default=unicode("{}"))

    handling_option = Column(Unicode(64), nullable=True)
    handling_cost_in_cents = Column(BigInteger, nullable=True, default=0)

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    active = Column(Boolean, default=False)

    # many to many uses association_proxy.
    coupons = association_proxy(
        "cart_coupons", "coupon", creator=lambda c: CartCoupon(coupon=c)
    )

    user = relationship(argument="User", uselist=False, lazy="joined")
    shop = relationship(argument="Shop", uselist=False, lazy="joined")

    def __init__(self, user=None):
        # since shopping carts are a private thing which may optionally
        # be granted public access, we use random uuid4 UUIDs to prevent
        # interative discovery/enumeration of public carts.
        self.id = uuid.uuid4()
        self.user = user
        self.json_cart = unicode("{}")
        self.created_timestamp = now_timestamp()
        self.updated_timestamp = now_timestamp()

    def _bust_memoized_attributes(self):
        if hasattr(self, "_count"):
            del self._count
        if hasattr(self, "_line_totals_in_cents"):
            del self._line_totals_in_cents
        if hasattr(self, "_products"):
            del self._products
        if hasattr(self, "_physical_products"):
            del self._physical_products
        if hasattr(self, "_shops"):
            del self._shops
        if hasattr(self, "_shop_product_dict"):
            del self._shop_product_dict
        if hasattr(self, "_shop_totals_in_cents"):
            del self._shop_totals_in_cents
        if hasattr(self, "_shop_totals"):
            del self._shop_totals
        if hasattr(self, "_discounted_shop_totals_in_cents"):
            del self._discounted_shop_totals_in_cents
        if hasattr(self, "_discounted_shop_totals"):
            del self._discounted_shop_totals
        if hasattr(self, "_line_totals"):
            del self._line_totals

    def set_cart(self, cart_dict):
        """Save cart_dict as JSON into json_cart."""
        self._cart = cart_dict
        self.json_cart = json.dumps(self._cart)
        self.updated_timestamp = now_timestamp()
        self._bust_memoized_attributes()

    def get_cart(self):
        """memoized dictionary of user's shopping cart."""
        if hasattr(self, "_cart") == False:
            self._cart = json.loads(self.json_cart)
        return self._cart

    cart = property(get_cart, set_cart)

    def empty(self):
        """removes all items from cart."""
        self.cart = {}
        self._bust_memoized_attributes()

    def add_product(self, product):
        quantity = 1
        if product.uuid_str in self.cart:
            quantity = self.cart[product.uuid_str] + 1
        self.set_product_quantity(product, quantity)

    def remove_product(self, product):
        tmp_cart = self.cart
        if product.uuid_str in tmp_cart:
            del tmp_cart[product.uuid_str]
        self.cart = tmp_cart

    def set_product_quantity(self, product, quantity):
        quantity = int(quantity)
        if quantity >= 999:
            quantity = 999
        tmp_cart = self.cart
        tmp_cart[product.uuid_str] = quantity
        self.cart = tmp_cart

    def get_product_quantity(self, product):
        return self.cart.get(product.uuid_str, 0)

    def merge_in_cart(self, other):
        tmp_cart = self.cart
        for product_id, count in other.cart.items():
            if product_id in tmp_cart:
                tmp_cart[product_id] += count
            else:
                tmp_cart[product_id] = count

        self.handling_option = other.handling_option
        self.handling_cost_in_cents = self.handling_cost_in_cents

        for coupon in other.coupons:
            if coupon not in self.coupons:
                self.coupons.append(coupon)

        # this busts memoization.
        self.cart = tmp_cart

    @property
    def count(self):
        if hasattr(self, "_count") == False:
            self._count = sum(self.cart.values())
        return self._count

    @property
    def products(self):
        """
        Return a dictionary of unique Product objects in cart.

        The key is the product UUID, and the value is the Product object.
        """
        if hasattr(self, "_products") == False:
            product_ids = self.cart.keys()
            products = get_products_by_ids(self.dbsession, product_ids)
            self._products = bucket_objects_by_id(products)
        return self._products

    @property
    def physical_products(self):
        """
        Return a dictionary of physical Product objects in cart.

        The key is the product UUID, and the value is the Product object.
        """
        if not hasattr(self, "_physical_products"):
            self._physical_products = {}
            for product_id, product in self.products.items():
                if product.is_physical:
                    self._physical_products[product_id] = product
        return self._physical_products

    @property
    def shops(self):
        """
        Return a dictionary of unique Shop objects in cart.

        The key is the Shop UUID, and the value is the Shop object.
        """
        if hasattr(self, "_shops") == False:
            self._shops = {}

            # loop over Products in cart, aggregate a unique set of shop_ids.
            shop_ids = set()
            for product in self.products.values():
                shop_ids.add(product.id_to_uuid_str(product.shop_id))

            shops = get_shops_by_ids(self.dbsession, shop_ids)

            self._shops = bucket_objects_by_id(shops)

        return self._shops

    @property
    def shop_product_dict(self):
        """
        Return a dict where keys are shop_ids (as strings) and values are a list of tuples (product, quantity).
        """
        if not hasattr(self, "_shop_product_dict"):
            self._shop_product_dict = {}

            for product_id, quantity in self.cart.items():
                product = self.products[product_id]
                shop_id = product.shop.uuid_str
                if shop_id not in self._shop_product_dict:
                    self._shop_product_dict[shop_id] = []
                self._shop_product_dict[shop_id].append((product, quantity))

        return self._shop_product_dict

    @property
    def line_totals_in_cents(self):
        if hasattr(self, "_line_totals_in_cents") == False:
            self._line_totals_in_cents = {}
            for product in self.products.values():
                quantity = self.get_product_quantity(product)
                self._line_totals_in_cents[product.uuid_str] = (
                    product.price_in_cents * quantity
                )
        return self._line_totals_in_cents

    @property
    def line_totals(self):
        if hasattr(self, "_line_totals") == False:
            self._line_totals = {}
            for product_id, line_total_in_cents in self.line_totals_in_cents.items():
                self._line_totals[product_id] = cents_to_dollars(line_total_in_cents)
        return self._line_totals

    @property
    def shop_totals_in_cents(self):
        if not hasattr(self, "_shop_totals_in_cents"):
            self._shop_totals_in_cents = {}
            for shop_id, product_quantity_tuple in self.shop_product_dict.items():
                self._shop_totals_in_cents[shop_id] = 0
                for product, _ in product_quantity_tuple:
                    self._shop_totals_in_cents[shop_id] += self.line_totals_in_cents[
                        product.uuid_str
                    ]
        return self._shop_totals_in_cents

    @property
    def shop_totals(self):
        if hasattr(self, "_shop_totals") == False:
            self._shop_totals = {}
            for shop_id, shop_total_in_cents in self.shop_totals_in_cents.items():
                self._shop_totals[shop_id] = cents_to_dollars(shop_total_in_cents)
        return self._shop_totals

    @property
    def discounted_shop_totals_in_cents(self):
        """Discounted shop totals in cents after applying coupons."""
        if hasattr(self, "_discounted_shop_totals_in_cents") == False:
            from copy import deepcopy

            self._discounted_shop_totals_in_cents = deepcopy(self.shop_totals_in_cents)
            if len(self.coupons) > 0:
                for coupon in sorted(self.coupons, key=lambda c: c.id):
                    for (
                        shop_uuid,
                        shop_total_in_cents,
                    ) in self.shop_totals_in_cents.items():
                        if coupon.shop_uuid_str == shop_uuid:
                            self._discounted_shop_totals_in_cents[shop_uuid] = (
                                coupon.compute_discount(shop_total_in_cents)
                            )
        return self._discounted_shop_totals_in_cents

    @property
    def discounted_shop_totals(self):
        if hasattr(self, "_discounted_shop_totals") == False:
            self._discounted_shop_totals = {}
            for (
                shop_id,
                discounted_shop_total_in_cents,
            ) in self.discounted_shop_totals_in_cents.items():
                self._discounted_shop_totals[shop_id] = cents_to_dollars(
                    discounted_shop_total_in_cents
                )
        return self._discounted_shop_totals

    @property
    def total_price_in_cents(self):
        """
        Calculate the total price in cents, including handling cost if applicable.
        """
        total = sum(self.line_totals_in_cents.values())
        if self.handling_cost_in_cents:
            total += self.handling_cost_in_cents
        return total

    @property
    def total_price(self):
        """
        Total price in dollars, including handling cost if applicable.
        """
        return cents_to_dollars(self.total_price_in_cents)

    @property
    def total_discounted_price_in_cents(self):
        """
        Calculate the total discounted price in cents, including handling cost if applicable.
        """
        total = sum(self.discounted_shop_totals_in_cents.values())
        if self.handling_cost_in_cents:
            total += self.handling_cost_in_cents
        return total

    @property
    def total_discounted_price(self):
        """
        Total discounted price in dollars, including handling cost if applicable.
        """
        return cents_to_dollars(self.total_discounted_price_in_cents)

    @property
    def is_discounted(self):
        if self.total_price != self.total_discounted_price:
            return True
        return False

    @property
    def total(self):
        """
        The total in dollars (after discounts) to be charged to user via an Invoice, including handling cost if applicable.
        """
        if self.is_discounted:
            return self.total_discounted_price
        return self.total_price

    @property
    def total_in_cents(self):
        """
        The total in cents (after discounts) to be charged to user via an Invoice, including handling cost if applicable.
        """
        if self.is_discounted:
            return self.total_discounted_price_in_cents
        return self.total_price_in_cents

    @property
    def requires_payment(self):
        """Return True if we should charge a card, else False."""
        # Only charge a credit card if cart total is greater than $0.64!
        # Credit card "gas" payment costs $0.30 + 2.9%
        # We gift the customer up to $0.32 when we bypass credit card gas.
        if self.total_in_cents > 64:
            return True
        return False

    @property
    def is_not_public(self):
        return not self.public

    @property
    def is_empty(self):
        return self.count <= 0

    @property
    def human_updated_timestamp(self):
        return timestamp_to_ago_string(self.updated_timestamp)

    @property
    def human_created_timestamp(self):
        return timestamp_to_ago_string(self.created_timestamp)

    def validate_attached_coupons(self):
        """This routine makes sure all attached coupons have terms met."""
        error_messages = []
        if self.coupons:
            if len(self.coupons) > 1:
                error_messages.append(
                    "We don't support coupon stacking. Please choose one coupon."
                )
            for coupon in self.coupons:
                # test if the shop's cart total qualifies for this coupon.
                if coupon.is_not_valid:
                    error_messages.append(
                        f"Sorry, the coupon '{coupon.code}' is not valid (expired or disabled)."
                    )
                if self.shop_totals_in_cents.get(coupon.shop_uuid_str, 0) <= (
                    coupon.cart_qualifier or 0
                ):
                    error_messages.append(
                        f"Please review the terms for coupon '{coupon.code}': shop total not met."
                    )
                if (
                    coupon.max_redemptions
                    and coupon.redemptions.count() >= coupon.max_redemptions
                ):
                    error_messages.append(
                        f"The coupon '{coupon.code}' was used too many times. Please remove it."
                    )
                if (
                    coupon.max_redemptions_per_user
                    and coupon.redemptions.filter_by(user_id=self.user_id).count()
                    >= coupon.max_redemptions_per_user
                ):
                    error_messages.append(
                        f"You have already used the coupon '{coupon.code}'. Please remove it."
                    )
        return error_messages

    def check_inventory(self, shop_location):
        """
        Check if the shop location has enough quantity for each physical product in the cart.
        Returns a list of error messages if any product is out of stock.
        """
        error_messages = []
        for product_id, product in self.physical_products.items():
            quantity_needed = self.cart[product_id]
            inventory = get_inventory_by_product_and_shop_location(
                self.dbsession, product_id, shop_location.uuid_str
            )
            if inventory is None or inventory.quantity < quantity_needed:
                error_messages.append(
                    f"Not enough stock for {product.title}. Switch Shop Location and try again. Needed: {quantity_needed}, Available: {inventory.quantity if inventory else 0}"
                )
        return error_messages

    def remove_handling_if_no_physical_products(self):
        """
        Remove the handling option and cost if there are no physical products in the cart.
        """
        if not self.physical_products:
            self.handling_option = None
            self.handling_cost_in_cents = 0

    def update_handling_cost(self, shop_location):
        """
        Update the handling cost based on the provided shop location.
        """
        if self.handling_option:
            if self.handling_option == "local_pickup":
                self.handling_cost_in_cents = 0
            elif self.handling_option == "local_delivery":
                self.handling_cost_in_cents = shop_location.local_delivery_rate_in_cents
            elif self.handling_option == "local_shipping":
                self.handling_cost_in_cents = shop_location.local_shipping_rate_in_cents
            elif self.handling_option == "international_shipping":
                self.handling_cost_in_cents = (
                    shop_location.international_shipping_rate_in_cents
                )

    def update_inventory(self, shop_location):
        """
        Update the inventory quantity for physical products in the cart.
        """
        changed = False
        for product_id, product in self.physical_products.items():
            quantity_needed = self.cart[product_id]
            inventory = get_inventory_by_product_and_shop_location(
                self.dbsession, product_id, shop_location.uuid_str
            )
            if inventory:
                inventory.quantity -= quantity_needed
                self.dbsession.add(inventory)
                changed = True

        if changed:
            self.dbsession.flush()


def get_all_carts(dbsession):
    """
    Return all Cart objects in descending order by
    created timestamp (newest first).
    """
    return dbsession.query(Cart).order_by(Cart.created_timestamp.desc())


def get_cart_by_id(dbsession, cart_id):
    """Try to get Cart object by id or return None."""
    return get_object_by_id(dbsession, cart_id, Cart)
