import uuid

from sqlalchemy import Column, BigInteger, Boolean, Integer, UnicodeText, Unicode

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp, get_object_by_id

from sqlalchemy.orm import relationship

from .coupon_redemption import CouponRedemption

from ..lib.currency import cents_to_dollars


class InvoiceLineItem(RBase, Base):
    """
    An invoice may have zero or many line items
    We should do our best to treat these line items as immutable.
    This will let us rely on them as a proof of transactional record.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    # a way to group multiple transactions into a single reference.
    invoice_id = Column(UUIDType, foreign_key("Invoice", "id"), nullable=False)
    # the product of this transaction.
    product_id = Column(UUIDType, foreign_key("Product", "id"), nullable=False)
    # the price object which was active during this transaction.
    price_id = Column(UUIDType, foreign_key("Price", "id"), nullable=False)
    # the shop who owns this product.
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    # optional, used to keep track of market place sales.
    market_id = Column(UUIDType, foreign_key("Market", "id"), nullable=True)
    # the amount of this product which was purchased (or credited).
    quantity = Column(Integer, nullable=False, default=1)
    # a credit basically represents a refund, we don't change the original
    # invoice item, but instead append a new line item flagged as a credit.
    credit = Column(Boolean, default=False)
    # the timestamp when this line_item was created.
    created_timestamp = Column(BigInteger, nullable=False)

    # one to one.
    invoice = relationship(argument="Invoice", uselist=False, lazy="joined")

    # one to one.
    product = relationship(argument="Product", uselist=False, lazy="joined")

    # one to one.
    price = relationship(argument="Price", uselist=False, lazy="joined")

    # one to one.
    shop = relationship(argument="Shop", uselist=False, lazy="joined")

    # one to one.
    market = relationship(argument="Market", uselist=False, lazy="joined")

    def __init__(
        self,
        invoice,
        product,
        price=None,
        shop=None,
        market=None,
        quantity=1,
        credit=False,
    ):
        if price is None:
            price = product.current_price
        if shop is None:
            shop = product.shop

        self.id = uuid.uuid1()
        self.invoice = invoice
        self.product = product
        self.price = price
        self.shop = shop
        self.market = market
        self.quantity = quantity
        self.credit = credit
        self.created_timestamp = now_timestamp()


class Invoice(RBase, Base):
    """
    A user may have zero or many invoices
    which relate to a purchase transaction.
    """

    id = Column(UUIDType, primary_key=True, index=True)
    # the user making the purchase.
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    # the shop for this invoice, null if a marketplace sale.
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=True)
    # optional, opt-in, a marketplace may sell products on behalf of a shop.
    # the marketplace is responsible for charging the customer
    # and paying out the shop owner, while taking a 15-35% cut.
    market_id = Column(UUIDType, foreign_key("Market", "id"), nullable=True)
    # the timestamp when the invoice was created.
    created_timestamp = Column(BigInteger, nullable=False)

    # optional physical product handling.
    handling_option = Column(Unicode(64), nullable=True)
    handling_cost_in_cents = Column(BigInteger, nullable=True, default=0)

    # denormalized address of user for shipping products.
    delivery_address = Column(UnicodeText, nullable=True)

    # PayPal payment tracking (nullable - only set for PayPal payments)
    paypal_order_id = Column(Unicode(64), nullable=True)
    paypal_capture_id = Column(Unicode(64), nullable=True)

    # Stripe payment tracking (nullable - only set for Stripe payments)
    stripe_payment_intent_id = Column(Unicode(64), nullable=True)
    stripe_charge_id = Column(Unicode(64), nullable=True)

    # Adyen payment tracking (nullable - only set for Adyen payments)
    adyen_psp_reference = Column(Unicode(64), nullable=True)

    # one to one.
    user = relationship(argument="User", uselist=False, lazy="joined")

    # one to one.
    shop = relationship(argument="Shop", uselist=False, lazy="joined")

    # one to one.
    market = relationship(argument="Market", uselist=False, lazy="joined")

    # one to many.
    # returns all the InvoiceLineItems.
    # lazy="dynamic" returns a query object instead of an InstrumentedList.
    # this is ideal when we want to further filter the results.
    line_items = relationship(
        argument="InvoiceLineItem", lazy="dynamic", back_populates="invoice"
    )

    # one to many.
    # returns all the CouponRedemptions for this Invoice.
    # lazy="dynamic" returns a query object instead of an InstrumentedList.
    # this is ideal when we want to further filter the results.
    coupon_redemptions = relationship(
        argument="CouponRedemption", lazy="dynamic", back_populates="invoice"
    )

    # maybe not needed anymore, an invoice is only good for one shop.
    # so multiple shops in a cart will mean multiple invoices.
    # TODO: We need a way to relate none or many CouponRedemption
    #       to an Invoice. This will allow us to keep track of where the
    #       coupons are utilized and how they affect the invoice total.
    #       When we have a concept of market places, we will need to make
    #       sure a shop coupon for say $5 will only affect products in the
    #       invoice related to that shop. Spending a $5 coupon from shop X
    #       on an market invoice total of $6 but only has a $2 product
    #       from shop X would bring the invoice total to $4.
    #       Shop coupon codes should only affect the "sub total" of that
    #       shop on the Invoice.

    def __init__(self, user):
        self.id = uuid.uuid1()
        self.user = user
        self.created_timestamp = now_timestamp()

    def new_line_item(self, product, quantity=1, market=None):
        """
        given a a product, and optional arguments attach a line item to this invoice.
        """
        self.line_items.append(
            InvoiceLineItem(
                invoice=self,
                product=product,
                quantity=quantity,
                market=market,
            )
        )

    def credit_line_item(self, line_item, quantity=None):
        """
        given a line_item, attach a credit/refund line item to this invoice.
        """
        if quantity is None:
            # By default we use the quantity from the `line_item`.
            # Lets say the given `line_item` has `quantity` of 3 and you want
            # to credit or refund the user only 1 of the 3. To do so, you
            # would pass `quantity=1` to `credit_line_item`.
            quantity = line_item.quantity

        self.line_items.append(
            InvoiceLineItem(
                invoice=self,
                product=line_item.product,
                price=line_item.price,
                shop=line_item.shop,
                market=line_item.market,
                quantity=quantity,
                credit=True,
            )
        )

    def new_coupon_redemption(self, coupon):
        """
        given a Coupon, create a coupon redemption for this invoice.
        """
        # TODO: currently this routine is naive to "market" invoices, an Invoice
        # which has InvoiceLineItems for Products derived from more than one Shop.
        if coupon.shop == self.shop:
            self.coupon_redemptions.append(
                CouponRedemption(
                    coupon=coupon,
                    invoice=self,
                    shop=coupon.shop,
                    user=self.user,
                )
            )

    @property
    def subtotal_in_cents(self):
        """Calculate the subtotal amount in cents for the invoice before discounts."""
        return sum(
            item.price.price_in_cents * item.quantity for item in self.line_items
        )

    @property
    def discount_amount_in_cents(self):
        """Calculate total discount amount from coupon redemptions."""
        discount = 0
        subtotal = self.subtotal_in_cents

        for redemption in self.coupon_redemptions:
            coupon = redemption.coupon
            if coupon.is_valid:
                # Apply coupon discount to subtotal
                discounted_subtotal = coupon.compute_discount(subtotal)
                # Calculate how much was discounted
                discount += subtotal - discounted_subtotal
                # Update subtotal for next coupon (if multiple coupons allowed)
                subtotal = discounted_subtotal

        return discount

    @property
    def total_in_cents(self):
        """Calculate the total amount in cents for the invoice, including handling fee and discounts."""
        subtotal = self.subtotal_in_cents
        discount = self.discount_amount_in_cents
        handling = self.handling_cost_in_cents or 0

        total = subtotal - discount + handling
        # Never go negative
        return max(0, total)

    @property
    def total(self):
        """Total in dollars."""
        return cents_to_dollars(self.total_in_cents)

    @property
    def requires_payment(self):
        """Return True if we should charge a card, else False."""
        # Only charge a credit card if invoice total is greater than $0.64!
        # Credit card "gas" payment costs $0.30 + 2.9%
        # We gift the customer up to $0.32 when we bypass credit card gas.
        if self.total_in_cents > 64:
            return True
        return False

    @property
    def human_created_timestamp(self):
        """Return the created timestamp in a human-readable format."""
        from datetime import datetime

        return datetime.fromtimestamp(self.created_timestamp / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @property
    def payment_status(self):
        """Get payment status from crypto_payment or assume paid for Stripe/PayPal."""
        if hasattr(self, "crypto_payment") and self.crypto_payment:
            return self.crypto_payment.status
        else:
            # If invoice exists without crypto_payment, it's a successful Stripe/PayPal payment
            return "paid"

    @property
    def payment_method(self):
        """Get payment method: crypto, paypal, or stripe."""
        try:
            if hasattr(self, "crypto_payment") and self.crypto_payment:
                # crypto_payment is a collection, get the first one
                if (
                    hasattr(self.crypto_payment, "__len__")
                    and len(self.crypto_payment) > 0
                ):
                    return self.crypto_payment[0].coin_type.lower()
                elif hasattr(self.crypto_payment, "coin_type"):
                    return self.crypto_payment.coin_type.lower()
        except Exception:
            pass
        # Check for PayPal payment
        if self.paypal_order_id:
            return "paypal"
        # Check for Adyen payment
        if self.adyen_psp_reference:
            return "adyen"
        # Check for Stripe payment (or assume Stripe for legacy invoices)
        if self.stripe_payment_intent_id:
            return "stripe"
        # Default to stripe for legacy invoices without explicit payment tracking
        return "stripe"

    @property
    def is_paid(self):
        """Check if this invoice has been successfully paid."""
        return self.payment_status in [
            "confirmed",
            "confirmed-overpay",
            "confirmed-complete",
            "paid",
        ]


def get_invoice_by_id(dbsession, invoice_id):
    """Try to get Invoice object by id or return None."""
    return get_object_by_id(dbsession, invoice_id, Invoice)


def get_invoice_by_paypal_order_id(dbsession, paypal_order_id):
    """Try to get Invoice object by PayPal order ID or return None."""
    return dbsession.query(Invoice).filter(
        Invoice.paypal_order_id == paypal_order_id
    ).first()


def get_invoice_by_stripe_payment_intent_id(dbsession, payment_intent_id):
    """Try to get Invoice object by Stripe payment intent ID or return None."""
    return dbsession.query(Invoice).filter(
        Invoice.stripe_payment_intent_id == payment_intent_id
    ).first()


def get_invoice_by_adyen_psp_reference(dbsession, psp_reference):
    """Try to get Invoice object by Adyen PSP reference or return None."""
    return dbsession.query(Invoice).filter(
        Invoice.adyen_psp_reference == psp_reference
    ).first()


def delete_invoice_by_id(dbsession, invoice_id):
    """
    Safely delete an invoice and its line items, but only if it's from a terminated/unsuccessful crypto payment.

    This function guards against deleting:
    1. Stripe invoices (contain important financial data)
    2. Successful crypto payment invoices (legitimate transactions)

    Only failed/terminated crypto payments should have their invoices deleted to clean up
    unsuccessful transactions. Successful crypto payments should keep their invoices as
    proof of purchase.

    Args:
        dbsession: Database session
        invoice_id: UUID of the invoice to delete

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "deleted": bool
        }
    """
    try:
        # Get the invoice
        invoice = get_invoice_by_id(dbsession, invoice_id)
        if not invoice:
            return {"success": False, "message": "Invoice not found", "deleted": False}

        # Check if this has an associated crypto payment
        # Query directly for crypto payments to ensure we get them
        from .crypto_payment import CryptoPayment

        crypto_payment = (
            dbsession.query(CryptoPayment)
            .filter(CryptoPayment.invoice_id == invoice_id)
            .first()
        )
        # Guard: Only delete if this is a crypto payment invoice
        if not crypto_payment:
            return {
                "success": False,
                "message": "Cannot delete non-crypto invoices - may contain important financial data",
                "deleted": False,
            }

        # Import CryptoPayment to access TERMINAL_STATUSES
        from .crypto_payment import CryptoPayment

        # Guard: Only delete invoices for terminated/unsuccessful crypto payments
        if crypto_payment.status not in CryptoPayment.TERMINAL_STATUSES:
            return {
                "success": False,
                "message": f"Cannot delete invoice for active crypto payment (status: {crypto_payment.status})",
                "deleted": False,
            }

        # Guard: Don't delete successful payments - those are legitimate transactions
        successful_statuses = ["confirmed", "confirmed-overpay", "confirmed-complete"]
        if crypto_payment.status in successful_statuses:
            return {
                "success": False,
                "message": f"Cannot delete invoice for successful crypto payment (status: {crypto_payment.status})",
                "deleted": False,
            }

        # Safe to delete - this is a failed/terminated crypto payment
        # Delete line items first
        for line_item in invoice.line_items:
            dbsession.delete(line_item)

        # Delete coupon redemptions
        for coupon_redemption in invoice.coupon_redemptions:
            dbsession.delete(coupon_redemption)

        # Delete the invoice itself
        dbsession.delete(invoice)

        return {
            "success": True,
            "message": f"Successfully deleted failed crypto invoice {invoice_id} (payment status: {crypto_payment.status})",
            "deleted": True,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting invoice: {str(e)}",
            "deleted": False,
        }
