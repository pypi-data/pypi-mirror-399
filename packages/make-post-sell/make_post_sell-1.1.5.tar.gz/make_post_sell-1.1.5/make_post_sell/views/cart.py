from pyramid.view import view_config

from . import (
    user_required,
    get_referer_or_home,
    shop_is_ready_required,
)

from ..models.cart import get_cart_by_id
from ..models.product import get_product_by_id
from ..models.invoice import Invoice, InvoiceLineItem

from pyramid.httpexceptions import HTTPFound

from ..lib.mail import (
    send_purchase_email,
    send_sale_email,
)

import stripe
import traceback
from datetime import datetime


def get_cart_from_matchdict(request):
    """
    This function uses the cart_id from the url path
    and returns a Cart object from the database or None.

    If active_cart is the same cart as the url, we need not to query database.
    """
    if str(request.active_cart.id) == request.matchdict["cart_id"]:
        return request.active_cart
    else:
        return get_cart_by_id(request.dbsession, request.matchdict["cart_id"])


@view_config(route_name="user_carts", renderer="carts.j2")
@user_required()
def carts(request):
    return {}


def get_smart_purchase_redirect_url(invoices):
    """
    Determine the best redirect URL after purchase completion.

    Returns:
    - Product download URL if single digital product
    - Invoice URL if multiple products or physical products
    - General purchases page as fallback
    """
    import logging

    logger = logging.getLogger(__name__)

    # Handle single invoice with single digital product
    if len(invoices) == 1:
        invoice = invoices[0]
        line_items = list(invoice.line_items)

        logger.info(
            f"Smart redirect check - Invoice {invoice.id} has {len(line_items)} line items"
        )

        # Single digital product - redirect to download page
        if len(line_items) == 1:
            product = line_items[0].product
            logger.info(f"Single product: {product.title} (ID: {product.id})")
            logger.info(f"Is physical: {product.is_physical}")
            logger.info(f"Has product file: {product.has_product_file}")
            logger.info(f"Product extensions: {product.extensions}")

            # Check if it's a digital product with a file
            if not product.is_physical and product.has_product_file:
                redirect_url = f"/p/{product.id}/{product.slug}"
                logger.info(f"Redirecting to product page: {redirect_url}")
                return redirect_url
            else:
                if product.is_physical:
                    logger.info(f"Product is physical, redirecting to invoice")
                else:
                    logger.info(f"Digital product has no file, redirecting to invoice")

        # Multiple products or physical products - redirect to invoice
        return f"/invoice/{invoice.id}"

    # Multiple invoices - redirect to general purchases page
    return "/u/purchases"


def save_cart(request):
    if request.active_cart.is_empty == False:
        new_cart = request.shop.create_new_cart_for_user(request.user)
        msg = ("Cart saved for later.", "info")
        request.session.flash(msg)


@view_config(route_name="user_cart_save")
@user_required(
    flash_msg="To <b>save</b> your cart, please verify your email address below.",
    flash_level="info",
    redirect_to_route_name="join-or-log-in",
)
def cart_save(request):
    save_cart(request)
    return HTTPFound("/cart")


@view_config(route_name="user_cart_public")
@user_required()
def cart_public(request):
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif request.user.does_not_own_cart(cart):
        msg = ("You do not own that cart.", "error")

    else:
        msg = (
            "You made that cart public, you may now share the cart's link with others.",
            "success",
        )
        cart.public = True
        request.dbsession.add(cart)
        request.dbsession.flush()

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="user_cart_unpublic")
@user_required()
def cart_unpublic(request):
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif request.user.does_not_own_cart(cart):
        msg = ("You do not own that cart.", "error")

    else:
        msg = ("You made that cart private again.", "success")
        cart.public = False
        request.dbsession.add(cart)
        request.dbsession.flush()

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="user_cart_activate")
def cart_activate(request):
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif cart == request.active_cart:
        msg = ("This cart is already your active cart.", "success")

    # TODO: consider changing user.does_not_own_cart to
    # user.can_not_edit_cart and user.can_edit_cart to match shops/products.
    # this would also allow two different users the ability to edit a shared cart?
    # is consistancy in the names/verbs/actions important in this case?
    elif cart.is_not_public and (request.user and request.user.does_not_own_cart(cart)):
        msg = ("That cart is not public and you do not own that cart.", "error")

    elif request.user and request.user.owns_cart(cart):
        msg = ("You activated that cart.", "success")
        request.shop.make_cart_active_for_user(request.user, cart)

    else:
        msg = ("You made a copy and activated that public cart.", "success")
        new_cart = request.shop.create_new_cart_for_user(request.user)
        new_cart.merge_in_cart(cart)
        request.dbsession.add(new_cart)
        request.session.flash(msg)
        request.session["active_cart_id"] = new_cart.uuid_str
        return HTTPFound(f"/cart/{new_cart.id}")

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="user_cart_delete")
@user_required()
def cart_delete(request):
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif request.user.does_not_own_cart(cart):
        msg = ("You do not own that cart.", "error")

    elif cart.active:
        msg = ("You may not delete an active cart.", "error")

    else:
        msg = ("You deleted that cart.", "success")
        request.dbsession.delete(cart)
        request.dbsession.flush()
        request.session.flash(msg)
        return HTTPFound("/u/carts")

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="cart")
def cart(request):
    """Load active cart from session. Create cart if not in session."""
    return HTTPFound(f"/cart/{request.active_cart.id}")


@view_config(route_name="cart_by_id", renderer="cart.j2")
def cart_by_id(request):
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif (
        cart.user is None
        or cart.public
        or (
            request.user and request.user.authenticated and request.user.owns_cart(cart)
        )
    ):
        # remove invalid coupons from cart, if any.
        for coupon in cart.coupons:
            if coupon.is_not_valid:
                cart.coupons.remove(coupon)
                request.dbsession.add(cart)
                request.dbsession.flush()
                msg = (
                    f"Invalid coupon ({coupon.code}) removed from cart.",
                    "info",
                )
                request.session.flash(msg)

        return {
            "cart": cart,
            "products": cart.products,
            "shops": cart.shops,
            "shop_product_dict": cart.shop_product_dict,
            "discounted_shop_totals": cart.discounted_shop_totals,
            "total_price": cart.total_price,
            "total_discounted_price": cart.total_discounted_price,
        }
    else:
        msg = (
            "You may not view that cart. It is not public and you do not own it.",
            "error",
        )

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="cart_add_product", request_method="POST", require_csrf=True)
def cart_add_product(request):
    product_id = request.params.get("product_id", None)

    if product_id is None:
        msg = ("missing product_id.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    product = get_product_by_id(request.dbsession, product_id)

    if request.user and request.user.does_not_own_cart(request.active_cart):
        msg = ("You do not own this cart.", "error")

    elif product is None:
        msg = ("invalid product_id.", "error")

    elif product.is_not_ready:
        msg = ("that product is not ready for purchase.", "error")

    elif product.is_not_sellable:
        msg = ("that content is not for sale or purchase.", "error")

    else:
        msg = (f'You added "{product.title}" to your cart.', "success")
        request.active_cart.add_product(product)
        request.dbsession.add(request.active_cart)
        request.dbsession.flush()
        request.session.flash(msg)
        return HTTPFound("/cart")

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="cart_remove_product", request_method="POST", require_csrf=True)
def cart_remove_product(request):
    product_id = request.params.get("product_id", None)

    if product_id is None:
        msg = ("missing product_id.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    product = get_product_by_id(request.dbsession, product_id)
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif request.user and request.user.does_not_own_cart(cart):
        msg = ("You do not own this cart.", "error")

    elif request.user is None and cart.user is not None:
        msg = ("You do not own this cart.", "error")

    elif request.user is None and cart.user is not None:
        msg = ("You do not own this cart.", "error")

    elif product is None:
        msg = ("That product_id does not exist.", "error")

    else:
        msg = (f'You removed "{product.title}" from the cart.', "success")
        cart.remove_product(product)
        cart.remove_handling_if_no_physical_products()
        request.dbsession.add(cart)
        request.dbsession.flush()

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(
    route_name="cart_quantity_product", request_method="POST", require_csrf=True
)
def cart_quantity_product(request):
    product_id = request.params.get("product_id", None)
    quantity = request.params.get("quantity", None)

    if quantity:
        try:
            quantity = int(quantity)
        except:
            msg = ("Quantity must be a positive integer.", "error")
            request.session.flash(msg)
            return HTTPFound(get_referer_or_home(request))

    if product_id is None or quantity is None or quantity == "":
        msg = ("missing product_id or quantity.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))
    elif int(quantity) <= 0:
        msg = ("Changed your mind? Click remove on the product.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    product = get_product_by_id(request.dbsession, product_id)
    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif request.user and request.user.does_not_own_cart(cart):
        msg = ("You do not own this cart.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    elif request.user is None and cart.user is not None:
        msg = ("You do not own this cart.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    elif product is None:
        msg = ("That product_id does not exist.", "error")
        request.session.flash(msg)

    # TODO: this should eventually switch to if not market request
    # then refuse to add a product of another shop.
    # we could keep a simple allow list of marketplace domains.
    elif not request.is_saas_domain and request.shop.uuid_str != product.shop_uuid_str:
        request.session.flash(
            ("Refusing to add a product from another shop to cart.", "error")
        )
        return HTTPFound("/cart")
    else:
        msg = (
            f'You updated the quantity of "{product.title}" in the cart.',
            "success",
        )
        cart.set_product_quantity(product, quantity)
        request.dbsession.add(cart)
        request.dbsession.flush()

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(
    route_name="cart_handling_option", request_method="POST", require_csrf=True
)
def cart_handling_option(request):
    cart = get_cart_from_matchdict(request)
    handling_option = request.params.get("handling_option")

    if request.user and request.user.does_not_own_cart(cart):
        request.session.flash(("You do not own this cart.", "error"))
        return HTTPFound(get_referer_or_home(request))

    if request.user is None and cart.user is not None:
        request.session.flash(("You do not own this cart.", "error"))
        return HTTPFound(get_referer_or_home(request))

    if handling_option not in [
        "local_pickup",
        "local_delivery",
        "local_shipping",
        "international_shipping",
    ]:
        request.session.flash(("Invalid handling option selected.", "error"))
        return HTTPFound(get_referer_or_home(request))

    cart.handling_option = handling_option
    cart.update_handling_cost(request.shop_location)

    request.dbsession.add(cart)
    request.dbsession.flush()

    request.session.flash(("Handling option set successfully.", "success"))
    return HTTPFound(f"/cart/{cart.id}")


@view_config(
    route_name="cart_checkout",
    renderer="cart_checkout.j2",
    request_method="POST",
    require_csrf=True,
)
@view_config(
    route_name="user_cart_checkout",
    renderer="cart_checkout.j2",
    request_method="POST",
    require_csrf=True,
)
@user_required(
    flash_msg="To <b>checkout</b> your cart, please verify your email address below.",
    flash_level="info",
    redirect_to_route_name="join-or-log-in",
)
@shop_is_ready_required()
def cart_checkout(request):
    stripe_user_shop = request.shop.stripe_user_shop(request.user)
    paypal_user_shop = request.shop.paypal_user_shop(request.user)

    if "cart_id" not in request.matchdict:
        return HTTPFound(f"/u/cart/{request.active_cart.id}/checkout")

    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif cart.is_not_public and request.user.does_not_own_cart(cart):
        msg = ("That cart is not public and you do not own that cart.", "error")

    elif cart.is_empty:
        msg = ("That cart is empty, you cannot checkout.", "error")

    else:
        # Validate coupons first
        error_messages = cart.validate_attached_coupons()
        if error_messages:
            for error_message in error_messages:
                request.session.flash((error_message, "error"))
            return HTTPFound(get_referer_or_home(request))

        # Check handling options, inventory, and address for physical products
        if cart.physical_products:
            inventory_errors = cart.check_inventory(request.shop_location)
            if inventory_errors:
                for error_message in inventory_errors:
                    request.session.flash((error_message, "error"))
                return HTTPFound(get_referer_or_home(request))

            if not cart.handling_option:
                msg = (
                    "Please select a handling option for your physical items.",
                    "error",
                )
                request.session.flash(msg)
                return HTTPFound(get_referer_or_home(request))

            if not request.user.active_address:
                msg = (
                    "Please add a shipping address to proceed with checkout.",
                    "info",
                )
                request.session.flash(msg)
                return HTTPFound("/u/addresses")

        # Check for payment information
        # Only force Stripe flow if Stripe is the ONLY enabled payment method
        only_stripe_enabled = (
            request.stripe_enabled
            and not request.paypal_enabled
            and not request.monero_enabled
            and not request.dogecoin_enabled
        )
        if cart.requires_payment and only_stripe_enabled and stripe_user_shop is None:
            msg = ("Please enter your payment information.", "info")
            request.session.flash(msg)
            return HTTPFound("/billing")

        if (
            only_stripe_enabled
            and stripe_user_shop
            and stripe_user_shop.active_card is None
        ):
            msg = ("Please make a payment method active.", "info")
            request.session.flash(msg)
            return HTTPFound("/billing")

        # Check if shop has enabled XMR crypto processor AND wallet is synced
        xmr_processor_enabled = False
        if request.monero_enabled and request.monero_synced:
            from ..models.crypto_processor import CryptoProcessor

            xmr_processor = (
                request.dbsession.query(CryptoProcessor)
                .filter(
                    CryptoProcessor.shop_id == request.shop.id,
                    CryptoProcessor.coin_type == "XMR",
                    CryptoProcessor.enabled == True,
                )
                .first()
            )
            xmr_processor_enabled = xmr_processor is not None

        # Check if shop has enabled DOGE crypto processor AND node is synced
        doge_processor_enabled = False
        if request.dogecoin_enabled and request.dogecoin_synced:
            from ..models.crypto_processor import CryptoProcessor

            doge_processor = (
                request.dbsession.query(CryptoProcessor)
                .filter(
                    CryptoProcessor.shop_id == request.shop.id,
                    CryptoProcessor.coin_type == "DOGE",
                    CryptoProcessor.enabled == True,
                )
                .first()
            )
            doge_processor_enabled = doge_processor is not None

        # Check for pending crypto quotes for this user
        from ..models.crypto_payment import CryptoPayment

        pending_quotes = []
        if request.user:
            # Look for pending crypto payments for this user's invoices
            pending_quotes = (
                request.dbsession.query(CryptoPayment)
                .join(CryptoPayment.invoice)
                .filter(
                    Invoice.user_id == request.user.id,
                    CryptoPayment.status.in_(["pending", "received"]),
                )
                .order_by(CryptoPayment.created_timestamp.desc())
                .limit(5)  # Show up to 5 most recent pending quotes
                .all()
            )

        msg = ("Please confirm your order.", "info")
        request.session.flash(msg)
        return {
            "cart": cart,
            "products": cart.products,
            "active_card": stripe_user_shop.active_card if stripe_user_shop else None,
            "stripe_enabled": request.stripe_enabled,
            "paypal_enabled": request.paypal_enabled,
            "paypal_user_shop": paypal_user_shop,
            "monero_enabled": request.monero_enabled,
            "monero_synced": request.monero_synced,
            "xmr_processor_enabled": xmr_processor_enabled,
            "dogecoin_enabled": request.dogecoin_enabled,
            "dogecoin_synced": request.dogecoin_synced,
            "doge_processor_enabled": doge_processor_enabled,
            "pending_crypto_quotes": pending_quotes,
        }

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))


@view_config(
    route_name="user_cart_complete_checkout", request_method="POST", require_csrf=True
)
@user_required()
@shop_is_ready_required()
def cart_complete_checkout(request):
    stripe_enabled = request.stripe_enabled

    cart = get_cart_from_matchdict(request)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_not_public and request.user.does_not_own_cart(cart):
        msg = ("That cart is not public and you do not own that cart.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_empty:
        msg = ("That cart is empty, you cannot checkout.", "error")
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    # If the cart requires payment and Stripe is disabled, this endpoint cannot process payment
    if cart.requires_payment and not request.stripe_enabled:
        msg = ("Card payments are disabled by configuration.", "error")
        request.session.flash(msg)
        return HTTPFound("/cart")

    # If Stripe is enabled and payment is required, ensure a Stripe customer exists
    if (
        cart.requires_payment
        and request.stripe_enabled
        and request.shop.stripe_customer(request.user) is None
    ):
        msg = ("Please enter your payment information.", "info")
        request.session.flash(msg)
        return HTTPFound("/billing")

    error_messages = cart.validate_attached_coupons()
    if error_messages:
        for error_message in error_messages:
            request.session.flash((error_message, "error"))
        return HTTPFound(get_referer_or_home(request))

    try:
        invoices = []

        # First, prepare invoices without persisting
        for shop_id, product_quantity_tuple in cart.shop_product_dict.items():
            shop = cart.shops[shop_id]
            invoice = Invoice(request.user)
            invoice.shop = shop
            invoice.shop_id = shop.id
            invoice.handling_option = cart.handling_option
            invoice.handling_cost_in_cents = cart.handling_cost_in_cents

            if cart.physical_products:
                invoice.delivery_address = request.user.active_address.data

            for product, quantity in product_quantity_tuple:
                invoice.new_line_item(product=product, quantity=quantity)

            for coupon in cart.coupons:
                invoice.new_coupon_redemption(coupon)

            invoices.append(invoice)

        # Attempt payment BEFORE adding invoices to session when Stripe is enabled
        if request.stripe_enabled:
            for invoice in invoices:
                shop = invoice.shop

                if invoice.requires_payment:
                    stripe_user_shop = shop.stripe_user_shop(request.user)
                    if stripe_user_shop is None:
                        msg = (
                            "Payment method required but not found. Please add a payment method.",
                            "error",
                        )
                        request.session.flash(msg)
                        return HTTPFound("/billing")

                    # Use idempotency key to prevent duplicate charges on retry
                    idempotency_key = f"checkout_{cart.uuid_str}_{shop.uuid_str}_{invoice.total_in_cents}"

                    payment_intent = shop.stripe.PaymentIntent.create(
                        amount=invoice.total_in_cents,
                        currency="usd",
                        customer=stripe_user_shop.cus_id,
                        payment_method=stripe_user_shop.active_card_id,
                        off_session=True,
                        confirm=True,
                        idempotency_key=idempotency_key,
                    )

                    # Store Stripe payment references on invoice
                    invoice.stripe_payment_intent_id = payment_intent.id
                    if payment_intent.latest_charge:
                        invoice.stripe_charge_id = payment_intent.latest_charge

        # Only persist data after successful payment
        for invoice in invoices:
            for line_item in invoice.line_items:
                line_item.product.unlock_for_user(request.user)
                request.dbsession.add(line_item.product)

            request.dbsession.add(invoice)

        cart.update_inventory(request.shop_location)
        msg = ("Success, you have completed the purchase!", "success")
        request.session.flash(msg)

        for invoice in invoices:
            send_purchase_email(
                request,
                request.user.email,
                [item.product for item in invoice.line_items],
                invoice.total,
            )
            send_sale_email(
                request,
                invoice.shop,
                [item.product for item in invoice.line_items],
                invoice.total,
            )

        save_cart(request)
        redirect_url = get_smart_purchase_redirect_url(invoices)
        return HTTPFound(redirect_url)

    except stripe.error.CardError as e:
        request.tm.abort()
        msg = ("Payment failed. Please check your card details.", "error")
        request.session.flash(msg)
        return HTTPFound("/billing")

    except Exception as e:
        request.tm.abort()
        msg = (f"Payment failed: {str(e)}", "error")
        request.session.flash(msg)
        return HTTPFound("/billing")


@view_config(
    route_name="paypal_complete_checkout", request_method="POST", require_csrf=True
)
@user_required()
@shop_is_ready_required()
def paypal_complete_checkout(request):
    """Complete checkout using PayPal payment."""
    if not request.paypal_enabled:
        request.session.flash(("PayPal payments are disabled.", "error"))
        return HTTPFound("/cart")

    cart = get_cart_from_matchdict(request)

    if cart is None:
        request.session.flash(("That cart_id does not exist.", "error"))
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_not_public and request.user.does_not_own_cart(cart):
        request.session.flash(("That cart is not public and you do not own that cart.", "error"))
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_empty:
        request.session.flash(("That cart is empty, you cannot checkout.", "error"))
        return HTTPFound(get_referer_or_home(request))

    error_messages = cart.validate_attached_coupons()
    if error_messages:
        for error_message in error_messages:
            request.session.flash((error_message, "error"))
        return HTTPFound(get_referer_or_home(request))

    paypal_order_ids_param = request.params.get("paypal_order_id")
    if not paypal_order_ids_param:
        request.session.flash(("PayPal order ID is missing.", "error"))
        return HTTPFound("/cart")

    paypal_order_ids = [oid.strip() for oid in paypal_order_ids_param.split(",")]

    successful_invoices = []
    failed_shops = []

    try:
        import requests

        invoice_map = {}
        for shop_id, product_quantity_tuple in cart.shop_product_dict.items():
            shop = cart.shops[shop_id]
            invoice = Invoice(request.user)
            invoice.shop = shop
            invoice.shop_id = shop.id
            invoice.handling_option = cart.handling_option
            invoice.handling_cost_in_cents = cart.handling_cost_in_cents

            if cart.physical_products:
                invoice.delivery_address = request.user.active_address.data

            for product, quantity in product_quantity_tuple:
                invoice.new_line_item(product=product, quantity=quantity)

            for coupon in cart.coupons:
                if hasattr(coupon, 'is_active') and not coupon.is_active:
                    continue
                invoice.new_coupon_redemption(coupon)

            invoice_map[shop_id] = invoice

        invoices_requiring_payment = [inv for inv in invoice_map.values() if inv.requires_payment]

        if len(paypal_order_ids) != len(invoices_requiring_payment):
            request.session.flash((f"PayPal order count mismatch.", "error"))
            return HTTPFound("/cart")

        for idx, invoice in enumerate(invoices_requiring_payment):
            shop = invoice.shop
            paypal_order_id = paypal_order_ids[idx]

            try:
                api = shop.paypal
                mode = api.mode if hasattr(api, 'mode') else 'sandbox'
                base_url = "https://api-m.sandbox.paypal.com" if mode == "sandbox" else "https://api-m.paypal.com"

                auth_response = requests.post(
                    f"{base_url}/v1/oauth2/token",
                    headers={"Accept": "application/json", "Accept-Language": "en_US"},
                    data={"grant_type": "client_credentials"},
                    auth=(shop.paypal_client_id, shop.paypal_secret)
                )

                if auth_response.status_code != 200:
                    failed_shops.append((shop, "Payment processor configuration error."))
                    continue

                access_token = auth_response.json()["access_token"]

                capture_response = requests.post(
                    f"{base_url}/v2/checkout/orders/{paypal_order_id}/capture",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    }
                )

                if capture_response.status_code not in [200, 201]:
                    failed_shops.append((shop, "Payment could not be processed."))
                    continue

                order = capture_response.json()

                try:
                    captured_amount = float(order["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"])
                    if abs(captured_amount - invoice.total) > 0.01:
                        failed_shops.append((shop, "Payment amount verification failed."))
                        continue
                except (KeyError, ValueError, IndexError):
                    failed_shops.append((shop, "Payment processing error."))
                    continue

                invoice.paypal_order_id = paypal_order_id

                if (
                    "purchase_units" in order
                    and len(order["purchase_units"]) > 0
                    and "payments" in order["purchase_units"][0]
                    and "captures" in order["purchase_units"][0]["payments"]
                    and len(order["purchase_units"][0]["payments"]["captures"]) > 0
                ):
                    invoice.paypal_capture_id = order["purchase_units"][0]["payments"]["captures"][0]["id"]

                # Handle vaulting
                try:
                    if "payment_source" in order and "paypal" in order["payment_source"]:
                        paypal_source = order["payment_source"]["paypal"]
                        if "attributes" in paypal_source and "vault" in paypal_source["attributes"]:
                            vault_info = paypal_source["attributes"]["vault"]
                            if vault_info.get("status") == "VAULTED" and vault_info.get("id"):
                                from ..models.paypal_user_shop import PayPalUserShop
                                paypal_user_shop = shop.paypal_user_shop(request.user)
                                if paypal_user_shop is None:
                                    paypal_user_shop = PayPalUserShop(user=request.user, shop=shop)
                                    request.dbsession.add(paypal_user_shop)
                                paypal_user_shop.active_payment_token = vault_info["id"]
                                if "payer" in order and "payer_id" in order["payer"]:
                                    paypal_user_shop.payer_id = order["payer"]["payer_id"]
                                request.dbsession.add(paypal_user_shop)
                except Exception:
                    pass

                for line_item in invoice.line_items:
                    line_item.product.unlock_for_user(request.user)
                    request.dbsession.add(line_item.product)

                request.dbsession.add(invoice)
                successful_invoices.append(invoice)

            except Exception as e:
                failed_shops.append((shop, f"Unexpected error: {str(e)}"))
                continue

        if successful_invoices:
            for invoice in successful_invoices:
                for line_item in invoice.line_items:
                    cart.remove_product(line_item.product, line_item.quantity)
            cart.update_inventory(request.shop_location)

            for invoice in successful_invoices:
                send_purchase_email(
                    request,
                    request.user.email,
                    [item.product for item in invoice.line_items],
                    invoice.total,
                )
                send_sale_email(
                    request,
                    invoice.shop,
                    [item.product for item in invoice.line_items],
                    invoice.total,
                )

        if successful_invoices and not failed_shops:
            request.session.flash(("Success! You have completed the purchase.", "success"))
        elif successful_invoices and failed_shops:
            request.session.flash(("Partial success. Some payments failed.", "warning"))
            for shop, error_msg in failed_shops:
                request.session.flash((f"{shop.name}: {error_msg}", "error"))
        else:
            request.session.flash(("All payments failed.", "error"))
            for shop, error_msg in failed_shops:
                request.session.flash((f"{shop.name}: {error_msg}", "error"))

        save_cart(request)

        if successful_invoices:
            return HTTPFound(get_smart_purchase_redirect_url(successful_invoices))
        return HTTPFound("/cart")

    except Exception as e:
        request.tm.abort()
        request.session.flash((f"Payment processing failed: {str(e)}", "error"))
        return HTTPFound("/cart")


@view_config(route_name="adyen_create_session", request_method="POST", renderer="json")
@user_required()
@shop_is_ready_required()
def adyen_create_session(request):
    """Create Adyen checkout session(s) for the cart."""
    if not getattr(request, "adyen_enabled", False):
        return {"error": "Adyen payments are disabled"}

    cart = get_cart_from_matchdict(request)

    if cart is None:
        return {"error": "Cart not found"}

    if cart.is_empty:
        return {"error": "Cart is empty"}

    try:
        sessions = []

        invoice_map = {}
        for shop_id, product_quantity_tuple in cart.shop_product_dict.items():
            shop = cart.shops[shop_id]

            invoice = Invoice(request.user)
            invoice.shop = shop
            invoice.shop_id = shop.id
            invoice.handling_option = cart.handling_option
            invoice.handling_cost_in_cents = cart.handling_cost_in_cents

            if cart.physical_products:
                invoice.delivery_address = request.user.active_address.data

            for product, quantity in product_quantity_tuple:
                invoice.new_line_item(product=product, quantity=quantity)

            for coupon in cart.coupons:
                invoice.new_coupon_redemption(coupon)

            invoice_map[shop_id] = invoice

        for shop_id, invoice in invoice_map.items():
            shop = invoice.shop

            if not shop.adyen or not shop.is_adyen_ready:
                return {"error": f"Adyen is not configured for shop: {shop.name}"}

            # Create Adyen checkout session
            adyen = shop.adyen
            result = adyen.checkout.payments_api.sessions({
                "amount": {
                    "currency": "USD",
                    "value": invoice.total_in_cents
                },
                "reference": f"cart_{cart.uuid_str}_{shop.uuid_str}",
                "merchantAccount": shop.adyen_merchant_account,
                "returnUrl": f"{request.host_url}/adyen/complete-checkout/{cart.id}",
                "shopperReference": request.user.uuid_str,
                "shopperEmail": request.user.email,
            })

            if result.status_code == 201:
                session_data = result.message
                sessions.append({
                    "shop_id": shop.uuid_str,
                    "session_id": session_data.get("id"),
                    "session_data": session_data.get("sessionData"),
                    "client_key": shop.adyen_client_key,
                })
            else:
                return {"error": f"Failed to create Adyen session for {shop.name}"}

        return {"sessions": sessions}

    except Exception as e:
        return {"error": str(e)}


@view_config(
    route_name="adyen_complete_checkout", request_method="POST", require_csrf=True
)
@user_required()
@shop_is_ready_required()
def adyen_complete_checkout(request):
    """Complete checkout using Adyen payment."""
    if not getattr(request, "adyen_enabled", False):
        request.session.flash(("Adyen payments are disabled.", "error"))
        return HTTPFound("/cart")

    cart = get_cart_from_matchdict(request)

    if cart is None:
        request.session.flash(("That cart_id does not exist.", "error"))
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_not_public and request.user.does_not_own_cart(cart):
        request.session.flash(("That cart is not public and you do not own that cart.", "error"))
        return HTTPFound(get_referer_or_home(request))

    elif cart.is_empty:
        request.session.flash(("That cart is empty, you cannot checkout.", "error"))
        return HTTPFound(get_referer_or_home(request))

    error_messages = cart.validate_attached_coupons()
    if error_messages:
        for error_message in error_messages:
            request.session.flash((error_message, "error"))
        return HTTPFound(get_referer_or_home(request))

    # Get PSP references from Adyen redirectResultCode or params
    psp_references_param = request.params.get("psp_references")
    if not psp_references_param:
        request.session.flash(("Adyen payment reference is missing.", "error"))
        return HTTPFound("/cart")

    psp_references = [ref.strip() for ref in psp_references_param.split(",")]

    successful_invoices = []
    failed_shops = []

    try:
        invoice_map = {}
        for shop_id, product_quantity_tuple in cart.shop_product_dict.items():
            shop = cart.shops[shop_id]
            invoice = Invoice(request.user)
            invoice.shop = shop
            invoice.shop_id = shop.id
            invoice.handling_option = cart.handling_option
            invoice.handling_cost_in_cents = cart.handling_cost_in_cents

            if cart.physical_products:
                invoice.delivery_address = request.user.active_address.data

            for product, quantity in product_quantity_tuple:
                invoice.new_line_item(product=product, quantity=quantity)

            for coupon in cart.coupons:
                if hasattr(coupon, 'is_active') and not coupon.is_active:
                    continue
                invoice.new_coupon_redemption(coupon)

            invoice_map[shop_id] = invoice

        invoices_requiring_payment = [inv for inv in invoice_map.values() if inv.requires_payment]

        if len(psp_references) != len(invoices_requiring_payment):
            request.session.flash((f"Adyen payment reference count mismatch.", "error"))
            return HTTPFound("/cart")

        for idx, invoice in enumerate(invoices_requiring_payment):
            shop = invoice.shop
            psp_reference = psp_references[idx]

            try:
                # Verify the payment with Adyen
                adyen = shop.adyen
                payment_details = adyen.checkout.payments_api.get_result_of_payment_session({
                    "sessionId": psp_reference
                })

                if payment_details.status_code != 200:
                    failed_shops.append((shop, "Payment verification failed."))
                    continue

                result = payment_details.message
                result_code = result.get("resultCode", "")

                if result_code not in ["Authorised", "Received"]:
                    failed_shops.append((shop, f"Payment not authorized: {result_code}"))
                    continue

                # Store the PSP reference
                invoice.adyen_psp_reference = result.get("pspReference", psp_reference)

                for line_item in invoice.line_items:
                    line_item.product.unlock_for_user(request.user)
                    request.dbsession.add(line_item.product)

                request.dbsession.add(invoice)
                successful_invoices.append(invoice)

            except Exception as e:
                failed_shops.append((shop, f"Unexpected error: {str(e)}"))
                continue

        if successful_invoices:
            for invoice in successful_invoices:
                for line_item in invoice.line_items:
                    cart.remove_product(line_item.product, line_item.quantity)
            cart.update_inventory(request.shop_location)

            for invoice in successful_invoices:
                send_purchase_email(
                    request,
                    request.user.email,
                    [item.product for item in invoice.line_items],
                    invoice.total,
                )
                send_sale_email(
                    request,
                    invoice.shop,
                    [item.product for item in invoice.line_items],
                    invoice.total,
                )

        if successful_invoices and not failed_shops:
            request.session.flash(("Success! You have completed the purchase.", "success"))
        elif successful_invoices and failed_shops:
            request.session.flash(("Partial success. Some payments failed.", "warning"))
            for shop, error_msg in failed_shops:
                request.session.flash((f"{shop.name}: {error_msg}", "error"))
        else:
            request.session.flash(("All payments failed.", "error"))
            for shop, error_msg in failed_shops:
                request.session.flash((f"{shop.name}: {error_msg}", "error"))

        save_cart(request)

        if successful_invoices:
            return HTTPFound(get_smart_purchase_redirect_url(successful_invoices))
        return HTTPFound("/cart")

    except Exception as e:
        request.tm.abort()
        request.session.flash((f"Payment processing failed: {str(e)}", "error"))
        return HTTPFound("/cart")


@view_config(route_name="paypal_create_order", request_method="POST", renderer="json")
@user_required()
@shop_is_ready_required()
def paypal_create_order(request):
    """Create PayPal order(s) for the cart."""
    if not request.paypal_enabled:
        return {"error": "PayPal payments are disabled"}

    cart = get_cart_from_matchdict(request)

    if cart is None:
        return {"error": "Cart not found"}

    if cart.is_empty:
        return {"error": "Cart is empty"}

    try:
        import requests
        order_ids = []

        invoice_map = {}
        for shop_id, product_quantity_tuple in cart.shop_product_dict.items():
            shop = cart.shops[shop_id]

            invoice = Invoice(request.user)
            invoice.shop = shop
            invoice.shop_id = shop.id
            invoice.handling_option = cart.handling_option
            invoice.handling_cost_in_cents = cart.handling_cost_in_cents

            if cart.physical_products:
                invoice.delivery_address = request.user.active_address.data

            for product, quantity in product_quantity_tuple:
                invoice.new_line_item(product=product, quantity=quantity)

            for coupon in cart.coupons:
                invoice.new_coupon_redemption(coupon)

            invoice_map[shop_id] = invoice

        for shop_id, invoice in invoice_map.items():
            shop = invoice.shop

            if not shop.paypal or not shop.is_paypal_ready:
                return {"error": f"PayPal is not configured for shop: {shop.name}"}

            shop_total_dollars = invoice.total

            api = shop.paypal
            mode = api.mode if hasattr(api, 'mode') else 'sandbox'
            base_url = "https://api-m.sandbox.paypal.com" if mode == "sandbox" else "https://api-m.paypal.com"

            auth_response = requests.post(
                f"{base_url}/v1/oauth2/token",
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
                data={"grant_type": "client_credentials"},
                auth=(shop.paypal_client_id, shop.paypal_secret)
            )

            if auth_response.status_code != 200:
                return {"error": f"PayPal unavailable for {shop.name}."}

            access_token = auth_response.json()["access_token"]
            currency = getattr(shop, 'currency', None) or 'USD'
            save_paypal = request.params.get("save_paypal", "false") == "true"

            order_json = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": f"{shop_total_dollars:.2f}"
                    },
                    "description": f"Purchase from {shop.name}"
                }]
            }

            if save_paypal:
                order_json["payment_source"] = {
                    "paypal": {
                        "attributes": {
                            "vault": {
                                "store_in_vault": "ON_SUCCESS",
                                "usage_type": "MERCHANT"
                            }
                        },
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "user_action": "PAY_NOW"
                        }
                    }
                }

            order_response = requests.post(
                f"{base_url}/v2/checkout/orders",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json=order_json
            )

            if order_response.status_code not in [200, 201]:
                return {"error": f"Unable to create PayPal order for {shop.name}."}

            order_data = order_response.json()
            order_ids.append(order_data["id"])

        return {"order_ids": order_ids}

    except Exception as e:
        return {"error": str(e)}
