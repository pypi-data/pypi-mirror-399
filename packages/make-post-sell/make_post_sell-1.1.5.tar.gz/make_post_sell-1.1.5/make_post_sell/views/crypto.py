from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.response import Response

import sqlalchemy as sa

from ..models.cart import get_cart_by_id
from ..models.invoice import Invoice, delete_invoice_by_id
from ..models.crypto_payment import CryptoPayment

from ..lib.crypto_watcher.crypto_clients import (
    get_client_from_settings,
    get_dogecoin_client_from_settings,
)

from . import (
    user_required,
    shop_is_ready_required,
)

from decimal import Decimal

import json
import math
import time
import uuid as _uuid
import urllib.request


def check_user_has_pending_quotes(request):
    """
    Check if the current user has any pending crypto quotes.
    Returns (has_pending, pending_payments) tuple.
    """
    if not request.user:
        return False, []

    from ..models.crypto_payment import CryptoPayment

    # Check for any crypto payments in pending or received status
    pending_payments = (
        request.dbsession.query(CryptoPayment)
        .filter(
            CryptoPayment.user_id == request.user.id,
            CryptoPayment.status.in_(
                [CryptoPayment.STATUS_PENDING, CryptoPayment.STATUS_RECEIVED]
            ),
        )
        .all()
    )

    return len(pending_payments) > 0, pending_payments


@view_config(
    route_name="crypto_xmr_start",
    request_method="POST",
    require_csrf=True,
    renderer="crypto_checkout.j2",
)
def crypto_xmr_start(request):
    # Check Monero enabled toggle first (no DB access)
    if not request.monero_enabled:
        request.session.flash(
            ("Monero payments are disabled by configuration.", "error")
        )
        return HTTPFound("/cart")

    cart_id = request.params.get("cart_id")
    if not cart_id:
        request.session.flash(("Missing cart_id.", "error"))
        return HTTPFound("/cart")

    # First database access - this establishes the transaction
    cart = get_cart_by_id(request.dbsession, cart_id)
    if cart is None:
        request.session.flash(("Invalid cart.", "error"))
        return HTTPFound("/cart")

    # Now check user authentication (after DB transaction is established)
    if not (request.user and request.user.authenticated):
        request.session.flash(
            ("To use Monero checkout, please verify your email.", "info")
        )
        return HTTPFound(request.route_url("join-or-log-in"))

    # Check if user has any pending crypto quotes (any coin type)
    has_pending, pending_payments = check_user_has_pending_quotes(request)
    if has_pending:
        coin_types = list(set([p.coin_type for p in pending_payments]))
        coin_list = ", ".join(coin_types)
        request.session.flash(
            (
                f"You have pending {coin_list} payment(s). Please complete or cancel them before starting a new quote.",
                "warning",
            )
        )
        return HTTPFound(request.route_url("crypto_history"))

    # Now check if shop is ready for payment (after DB transaction is established)
    if not (request.shop and request.shop.is_ready_for_payment(request)):
        request.session.flash(
            (
                "Sorry, this shop is not ready to make sales yet. Please try again later.",
                "error",
            )
        )
        from . import get_referer_or_home

        return HTTPFound(get_referer_or_home(request))

    if request.user.does_not_own_cart(cart):
        request.session.flash(("You do not own this cart.", "error"))
        return HTTPFound("/cart")

    # single-shop constraint for MVP
    if len(cart.shop_product_dict.keys()) != 1:
        request.session.flash(
            ("Monero checkout only supports single-shop carts.", "error")
        )
        return HTTPFound(f"/cart/{cart.id}")

    if not cart.requires_payment:
        request.session.flash(("No payment required for this order.", "info"))
        return HTTPFound(f"/cart/{cart.id}")

    # Ensure config exists; if not, provide a helpful message.
    settings = request.registry.settings
    if not settings.get("monero.rpc_url"):
        request.session.flash(
            (
                "Monero RPC not configured. Set monero.rpc_url in your ini to enable.",
                "error",
            )
        )
        return HTTPFound(f"/cart/{cart.id}")

    # Build a pending invoice for this single shop (do not unlock or send emails yet)
    try:
        # Extract the single shop and items
        (shop_id, items) = next(iter(cart.shop_product_dict.items()))
        shop = cart.shops[shop_id]

        invoice = Invoice(request.user)
        invoice.shop = shop
        invoice.shop_id = shop.id
        invoice.handling_option = cart.handling_option
        invoice.handling_cost_in_cents = cart.handling_cost_in_cents

        if cart.physical_products and request.user.active_address:
            invoice.delivery_address = request.user.active_address.data

        for product, quantity in items:
            invoice.new_line_item(product=product, quantity=quantity)

        for coupon in cart.coupons:
            invoice.new_coupon_redemption(coupon)

        # Check inventory for physical products BEFORE creating payment quote
        from ..models.inventory import get_inventory_by_product_and_shop_location

        out_of_stock_items = []

        if request.shop_location:
            for product, quantity in items:
                if getattr(product, "is_physical", False):
                    inv = get_inventory_by_product_and_shop_location(
                        request.dbsession, product.id, request.shop_location.id
                    )
                    available_qty = inv.quantity if inv else 0
                    if available_qty < quantity:
                        out_of_stock_items.append(
                            {
                                "product": product,
                                "requested": quantity,
                                "available": available_qty,
                            }
                        )

        # If any items are out of stock, redirect back to cart with error
        if out_of_stock_items:
            error_msg = "The following items are out of stock:\n"
            for item in out_of_stock_items:
                error_msg += f"- {item['product'].title}: requested {item['requested']}, available {item['available']}\n"
            request.session.flash((error_msg, "error"))
            return HTTPFound(f"/cart/{cart.id}")

        # Persist invoice now so we can link a CryptoPayment to it
        request.dbsession.add(invoice)
        request.dbsession.flush()

        # Fetch USD/XMR rate (with timeout/retry and sanity checks)
        rate_url = settings.get(
            "monero.rate_source_url",
            "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd",
        )
        last_err = None
        usd_per_xmr = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    rate_url, headers={"User-Agent": "make-post-sell/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as rate_resp:
                    rate_data = json.loads(rate_resp.read())
                candidate = float(rate_data.get("monero", {}).get("usd"))
                # sanity bounds: reject zero/negative/absurd values
                if not (0.01 <= candidate <= 100000.0):
                    raise RuntimeError("Out-of-bounds USD/XMR rate")
                usd_per_xmr = candidate
                break
            except Exception as e:
                last_err = e
                time.sleep(0.5)
        if usd_per_xmr is None:
            raise RuntimeError(f"Failed to fetch USD/XMR rate: {last_err}")

        # Compute piconero owed with dynamic transaction fee estimation
        usd_total = Decimal(str(invoice.total))
        xmr_amount = usd_total / Decimal(str(usd_per_xmr))
        # For fee estimation - use ceiling to avoid underestimating fees
        base_amount_piconero = math.ceil(xmr_amount * Decimal("1000000000000"))

        # Get dynamic fee estimate - we need the processor config first
        from ..models.crypto_processor import CryptoProcessor

        processor = (
            request.dbsession.query(CryptoProcessor)
            .filter(
                CryptoProcessor.shop_id == shop.id,
                CryptoProcessor.coin_type == "XMR",
                CryptoProcessor.enabled == True,
            )
            .first()
        )

        if processor and processor.sweep_to_address:
            # Use dynamic fee estimation with the actual sweep address
            fee_buffer_xmr = estimate_monero_fee_for_quote(
                settings, processor.sweep_to_address, base_amount_piconero
            )
        else:
            # Fallback to hardcoded fee if no processor configured yet
            fee_buffer_xmr = Decimal(settings.get("monero.fee_buffer", "0.0001"))

        xmr_amount_with_fee = xmr_amount + fee_buffer_xmr
        # Stay in Decimal arithmetic to avoid floating point precision issues
        expected_piconero = math.ceil(
            xmr_amount_with_fee * Decimal("1000000000000")
        )  # Round UP for quotes

        # Quote expiry - use shop-specific setting
        shop = invoice.shop
        expiry_secs = int(shop.crypto_quote_expiry_seconds)
        quote_expires_at_ms = int(time.time() * 1000) + (expiry_secs * 1000)

        # Check if invoice contains physical products
        has_physical = any(
            item.product.is_physical
            for item in invoice.line_items
            if hasattr(item.product, "is_physical")
        )

        if has_physical:
            # Physical products always require maximum confirmations
            confirmations_required = int(settings.get("monero.confirmations.high"))
        else:
            # Digital products: determine confirmations based on amount
            total_cents = invoice.total_in_cents

            # Use shop-specific risk thresholds
            shop = invoice.shop
            threshold_mid_cents = shop.payment_risk_threshold_mid_cents
            threshold_high_cents = shop.payment_risk_threshold_high_cents

            if total_cents < threshold_mid_cents:
                confirmations_required = int(settings.get("monero.confirmations.petty"))
            elif total_cents < threshold_high_cents:
                confirmations_required = int(settings.get("monero.confirmations.mid"))
            else:
                confirmations_required = int(settings.get("monero.confirmations.high"))

        # processor already queried above for fee estimation

        if not processor or processor.wallet_label is None:
            request.session.flash(("Shop has not configured Monero payments.", "error"))
            return HTTPFound(f"/cart/{cart.id}")

        # For Monero, wallet_label stores the account index as a string
        account_index = int(processor.wallet_label)

        client = get_client_from_settings(settings)
        label = f"shop:{shop.id}:invoice:{invoice.id}"
        address, subaddr_index = client.create_subaddress(
            account_index=account_index, label=label
        )

        # Get user's saved refund address for this coin type
        from ..models.user_crypto_refund_address import get_user_crypto_refund_address

        user_refund_addr_obj = get_user_crypto_refund_address(
            request.dbsession, request.user, request.shop, "XMR"
        )
        user_refund_address = (
            user_refund_addr_obj.address if user_refund_addr_obj else None
        )

        # Convert fee to atomic units (piconero) for storage
        estimated_fee_piconero = math.ceil(
            fee_buffer_xmr * Decimal("1000000000000")
        )  # Round UP for fees

        # Persist CryptoPayment
        crypto_payment = CryptoPayment(
            invoice=invoice,
            user=request.user,
            shop=shop,
            address=address,
            account_index=account_index,
            subaddress_index=subaddr_index,
            coin_type="XMR",
            expected_amount=expected_piconero,
            estimated_fee_amount=estimated_fee_piconero,
            rate_locked_usd_per_coin=usd_per_xmr,
            quote_expires_at_ms=quote_expires_at_ms,
            confirmations_required=confirmations_required,
            shop_location=request.shop_location,
            shop_sweep_to_address=processor.sweep_to_address,
            refund_address=user_refund_address,
        )
        request.dbsession.add(crypto_payment)
        request.dbsession.flush()

        # Redirect to generic quote page with payment UUID
        return HTTPFound(
            request.route_url("crypto_quote", payment_id=str(crypto_payment.id))
        )

    except Exception as e:
        request.session.flash((f"Failed to start Monero checkout: {e}", "error"))
        return HTTPFound(f"/cart/{cart.id}")


@view_config(
    route_name="crypto_doge_start",
    request_method="POST",
    require_csrf=True,
    renderer="crypto_checkout.j2",
)
def crypto_doge_start(request):
    # Check Dogecoin enabled toggle first (no DB access)
    if not request.dogecoin_enabled:
        request.session.flash(
            ("Dogecoin payments are disabled by configuration.", "error")
        )
        return HTTPFound("/cart")

    cart_id = request.params.get("cart_id")
    if not cart_id:
        request.session.flash(("Missing cart_id.", "error"))
        return HTTPFound("/cart")

    # First database access - this establishes the transaction
    cart = get_cart_by_id(request.dbsession, cart_id)
    if cart is None:
        request.session.flash(("Invalid cart.", "error"))
        return HTTPFound("/cart")

    # Now check user authentication (after DB transaction is established)
    if not (request.user and request.user.authenticated):
        request.session.flash(
            ("To use Dogecoin checkout, please verify your email.", "info")
        )
        return HTTPFound(request.route_url("join-or-log-in"))

    # Check if user has any pending crypto quotes (any coin type)
    has_pending, pending_payments = check_user_has_pending_quotes(request)
    if has_pending:
        coin_types = list(set([p.coin_type for p in pending_payments]))
        coin_list = ", ".join(coin_types)
        request.session.flash(
            (
                f"You have pending {coin_list} payment(s). Please complete or cancel them before starting a new quote.",
                "warning",
            )
        )
        return HTTPFound(request.route_url("crypto_history"))

    # Now check if shop is ready for payment (after DB transaction is established)
    if not (request.shop and request.shop.is_ready_for_payment(request)):
        request.session.flash(
            (
                "Sorry, this shop is not ready to make sales yet. Please try again later.",
                "error",
            )
        )
        from . import get_referer_or_home

        return HTTPFound(get_referer_or_home(request))

    if request.user.does_not_own_cart(cart):
        request.session.flash(("You do not own this cart.", "error"))
        return HTTPFound("/cart")

    # single-shop constraint for MVP
    if len(cart.shop_product_dict.keys()) != 1:
        request.session.flash(
            ("Dogecoin checkout only supports single-shop carts.", "error")
        )
        return HTTPFound(f"/cart/{cart.id}")

    if not cart.requires_payment:
        request.session.flash(("No payment required for this order.", "info"))
        return HTTPFound(f"/cart/{cart.id}")

    # Ensure config exists; if not, provide a helpful message.
    settings = request.registry.settings
    if not settings.get("dogecoin.rpc_url"):
        request.session.flash(
            (
                "Dogecoin RPC not configured. Set dogecoin.rpc_url in your ini to enable.",
                "error",
            )
        )
        return HTTPFound(f"/cart/{cart.id}")

    # Build a pending invoice for this single shop (do not unlock or send emails yet)
    try:
        # Extract the single shop and items
        (shop_id, items) = next(iter(cart.shop_product_dict.items()))
        shop = cart.shops[shop_id]

        invoice = Invoice(request.user)
        invoice.shop = shop
        invoice.shop_id = shop.id
        invoice.handling_option = cart.handling_option
        invoice.handling_cost_in_cents = cart.handling_cost_in_cents

        if cart.physical_products and request.user.active_address:
            invoice.delivery_address = request.user.active_address.data

        for product, quantity in items:
            invoice.new_line_item(product=product, quantity=quantity)

        for coupon in cart.coupons:
            invoice.new_coupon_redemption(coupon)

        # Check inventory for physical products BEFORE creating payment quote
        from ..models.inventory import get_inventory_by_product_and_shop_location

        out_of_stock_items = []

        if request.shop_location:
            for product, quantity in items:
                if getattr(product, "is_physical", False):
                    inv = get_inventory_by_product_and_shop_location(
                        request.dbsession, product.id, request.shop_location.id
                    )
                    available_qty = inv.quantity if inv else 0
                    if available_qty < quantity:
                        out_of_stock_items.append(
                            {
                                "product": product,
                                "requested": quantity,
                                "available": available_qty,
                            }
                        )

        # If any items are out of stock, redirect back to cart with error
        if out_of_stock_items:
            error_msg = "The following items are out of stock:\n"
            for item in out_of_stock_items:
                error_msg += f"- {item['product'].title}: requested {item['requested']}, available {item['available']}\n"
            request.session.flash((error_msg, "error"))
            return HTTPFound(f"/cart/{cart.id}")

        # Persist invoice now so we can link a CryptoPayment to it
        request.dbsession.add(invoice)
        request.dbsession.flush()

        # Fetch USD/DOGE rate (with timeout/retry and sanity checks)
        rate_url = settings.get(
            "dogecoin.rate_source_url",
            "https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd",
        )
        last_err = None
        usd_per_doge = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    rate_url, headers={"User-Agent": "make-post-sell/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as rate_resp:
                    rate_data = json.loads(rate_resp.read())
                candidate = float(rate_data.get("dogecoin", {}).get("usd"))
                # sanity bounds: reject zero/negative/absurd values (DOGE ranges from ~$0.01-$1.00)
                if not (0.001 <= candidate <= 100.0):
                    raise RuntimeError("Out-of-bounds USD/DOGE rate")
                usd_per_doge = candidate
                break
            except Exception as e:
                last_err = e
                time.sleep(0.5)
        if usd_per_doge is None:
            raise RuntimeError(f"Failed to fetch USD/DOGE rate: {last_err}")

        # Compute koinu (smallest unit) owed with dynamic transaction fee estimation
        usd_total = Decimal(str(invoice.total))
        doge_amount = usd_total / Decimal(str(usd_per_doge))

        # Use dynamic fee estimation for more accurate quotes
        fee_buffer_doge = estimate_dogecoin_fee_for_quote(settings)
        doge_amount_with_fee = doge_amount + fee_buffer_doge
        # Stay in Decimal arithmetic to avoid floating point precision issues
        expected_koinu = math.ceil(
            doge_amount_with_fee * Decimal("100000000")
        )  # Round UP for quotes

        # Quote expiry - use shop-specific setting
        shop = invoice.shop
        expiry_secs = int(shop.crypto_quote_expiry_seconds)
        quote_expires_at_ms = int(time.time() * 1000) + (expiry_secs * 1000)

        # Check if invoice contains physical products
        has_physical = any(
            item.product.is_physical
            for item in invoice.line_items
            if hasattr(item.product, "is_physical")
        )

        if has_physical:
            # Physical products always require maximum confirmations
            confirmations_required = int(
                settings.get("dogecoin.confirmations.high", "20")
            )
        else:
            # Digital products: determine confirmations based on amount
            total_cents = invoice.total_in_cents

            # Use shop-specific risk thresholds
            shop = invoice.shop
            threshold_mid_cents = shop.payment_risk_threshold_mid_cents
            threshold_high_cents = shop.payment_risk_threshold_high_cents

            if total_cents < threshold_mid_cents:
                confirmations_required = int(
                    settings.get("dogecoin.confirmations.petty", "2")
                )
            elif total_cents < threshold_high_cents:
                confirmations_required = int(
                    settings.get("dogecoin.confirmations.mid", "6")
                )
            else:
                confirmations_required = int(
                    settings.get("dogecoin.confirmations.high", "20")
                )

        # Get crypto processor configuration for this shop
        from ..models.crypto_processor import CryptoProcessor

        processor = (
            request.dbsession.query(CryptoProcessor)
            .filter(
                CryptoProcessor.shop_id == shop.id,
                CryptoProcessor.coin_type == "DOGE",
                CryptoProcessor.enabled == True,
            )
            .first()
        )

        if not processor or processor.wallet_label is None:
            request.session.flash(
                ("Shop has not configured Dogecoin payments.", "error")
            )
            return HTTPFound(f"/cart/{cart.id}")

        # For Dogecoin, wallet_label stores a label string for address generation
        wallet_label = processor.wallet_label

        client = get_dogecoin_client_from_settings(settings)
        address = client.getnewaddress(f"{wallet_label}:{invoice.id}")

        # Get user's saved refund address for this coin type
        from ..models.user_crypto_refund_address import get_user_crypto_refund_address

        user_refund_addr_obj = get_user_crypto_refund_address(
            request.dbsession, request.user, request.shop, "DOGE"
        )
        user_refund_address = (
            user_refund_addr_obj.address if user_refund_addr_obj else None
        )

        # Convert fee to atomic units (koinu) for storage
        estimated_fee_koinu = math.ceil(
            fee_buffer_doge * Decimal("100000000")
        )  # Round UP for fees

        # Persist CryptoPayment (using account_index=0, subaddress_index=0 for Bitcoin-like coins)
        crypto_payment = CryptoPayment(
            invoice=invoice,
            user=request.user,
            shop=shop,
            address=address,
            account_index=0,  # Not used for Bitcoin-like coins
            subaddress_index=0,  # Not used for Bitcoin-like coins
            coin_type="DOGE",
            expected_amount=expected_koinu,
            estimated_fee_amount=estimated_fee_koinu,
            rate_locked_usd_per_coin=usd_per_doge,
            quote_expires_at_ms=quote_expires_at_ms,
            confirmations_required=confirmations_required,
            shop_location=request.shop_location,
            shop_sweep_to_address=processor.sweep_to_address,
            refund_address=user_refund_address,
        )
        request.dbsession.add(crypto_payment)
        request.dbsession.flush()

        # Redirect to generic quote page with payment UUID
        return HTTPFound(
            request.route_url("crypto_quote", payment_id=str(crypto_payment.id))
        )

    except Exception as e:
        request.session.flash((f"Failed to start Dogecoin checkout: {e}", "error"))
        return HTTPFound(f"/cart/{cart.id}")


@view_config(
    route_name="crypto_quote",
    renderer="crypto_checkout.j2",
)
def crypto_quote(request):
    """Generic crypto quote page that works for any coin type"""
    payment_id = request.matchdict.get("payment_id")
    if not payment_id:
        request.session.flash(("Missing payment ID.", "error"))
        return HTTPFound("/cart")

    try:
        pid = _uuid.UUID(payment_id)
    except Exception:
        request.session.flash(("Invalid payment ID.", "error"))
        return HTTPFound("/cart")

    crypto_payment = (
        request.dbsession.query(CryptoPayment).filter(CryptoPayment.id == pid).first()
    )
    if not crypto_payment:
        request.session.flash(("Payment not found.", "error"))
        return HTTPFound("/cart")

    # Access control: allow purchaser or shop owners/editors
    user_can_access = False

    if request.user:
        # Allow the purchaser
        if crypto_payment.user_id == request.user.id:
            user_can_access = True
        # Allow shop owners/editors
        elif crypto_payment.shop and (
            request.user.can_edit_shop(crypto_payment.shop)
            or request.user.can_own_shop(crypto_payment.shop)
        ):
            user_can_access = True

    if not user_can_access:
        request.session.flash(
            ("Access denied. This quote is not accessible to you.", "error")
        )
        return HTTPFound("/")

    # Get coin-specific information
    coin_type = crypto_payment.coin_type
    coin_info = get_coin_info(coin_type)

    # Get user's refund address for this coin type
    from ..models.user_crypto_refund_address import get_user_crypto_refund_address

    user_refund_addr_obj = (
        get_user_crypto_refund_address(
            request.dbsession, request.user, request.shop, coin_type
        )
        if request.user
        else None
    )
    user_refund_address = user_refund_addr_obj.address if user_refund_addr_obj else None

    # Calculate amounts for display
    # For cancelled payments, invoice is None, so calculate USD total from locked rate
    if crypto_payment.invoice:
        usd_total = float(crypto_payment.invoice.total)
    else:
        # Calculate USD total from crypto amount and locked rate
        amount_crypto_with_fee = (
            crypto_payment.expected_amount / coin_info["smallest_unit_divisor"]
        )
        usd_total = float(
            amount_crypto_with_fee * float(crypto_payment.rate_locked_usd_per_coin)
        )

    amount_crypto_with_fee = (
        crypto_payment.expected_amount / coin_info["smallest_unit_divisor"]
    )

    # Use stored fee amount (calculated during payment creation) to avoid expensive RPC calls
    if crypto_payment.estimated_fee_amount is not None:
        # Convert stored atomic units back to coin units for display
        fee_buffer = (
            Decimal(crypto_payment.estimated_fee_amount)
            / coin_info["smallest_unit_divisor"]
        )
    else:
        # Fallback for old payments without stored fees
        settings = request.registry.settings
        fee_buffer = (
            float(
                settings.get(
                    f"{coin_type.lower()}.fee_buffer", coin_info["default_fee_buffer"]
                )
            )
            * 2
        )

    amount_crypto_base = amount_crypto_with_fee - float(fee_buffer)

    return {
        "cart": None,  # Quote page doesn't need cart context
        "address": crypto_payment.address,
        "coin_name": coin_info["name"],
        "coin_symbol": coin_type,
        "wallet_uri_scheme": coin_info["wallet_uri_scheme"],
        "smallest_unit_name": coin_info["smallest_unit_name"],
        "amount_crypto": amount_crypto_with_fee,
        "amount_crypto_base": amount_crypto_base,
        "fee_buffer_crypto": fee_buffer,
        "usd_total": usd_total,
        "usd_per_crypto": crypto_payment.rate_locked_usd_per_coin,
        "expected_smallest_units": crypto_payment.expected_amount,
        "expires_at": crypto_payment.quote_expires_at,
        "payment_id": str(crypto_payment.id),
        "status": crypto_payment.status,
        "current_confirmations": crypto_payment.current_confirmations or 0,
        "confirmations_required": crypto_payment.confirmations_required,
        "has_refund_address": bool(user_refund_address),
        "refund_address": user_refund_address,
        "now": int(time.time() * 1000),
        "terminal_statuses": list(CryptoPayment.TERMINAL_STATUSES),
        "refund_redirect_statuses": list(CryptoPayment.REFUND_REDIRECT_STATUSES),
        "has_invoice": bool(crypto_payment.invoice),
        "invoice_id": (
            str(crypto_payment.invoice.id) if crypto_payment.invoice else None
        ),
    }


def get_coin_info(coin_type):
    """Get coin-specific information"""
    coin_configs = {
        "XMR": {
            "name": "Monero",
            "wallet_uri_scheme": "monero",
            "smallest_unit_name": "piconero",
            "smallest_unit_divisor": 1_000_000_000_000,
            "default_fee_buffer": "0.0001",
        },
        "BTC": {
            "name": "Bitcoin",
            "wallet_uri_scheme": "bitcoin",
            "smallest_unit_name": "satoshi",
            "smallest_unit_divisor": 100_000_000,
            "default_fee_buffer": "0.00001",
        },
        "LTC": {
            "name": "Litecoin",
            "wallet_uri_scheme": "litecoin",
            "smallest_unit_name": "satoshi",
            "smallest_unit_divisor": 100_000_000,
            "default_fee_buffer": "0.00001",
        },
        "DOGE": {
            "name": "Dogecoin",
            "wallet_uri_scheme": "dogecoin",
            "smallest_unit_name": "koinu",
            "smallest_unit_divisor": 100_000_000,
            "default_fee_buffer": "0.01",
        },
    }
    return coin_configs.get(coin_type, coin_configs["XMR"])


@view_config(route_name="crypto_xmr_status")
@user_required()
def crypto_xmr_status(request):
    payment_id = request.matchdict.get("payment_id")
    if not payment_id:
        return HTTPBadRequest("missing payment_id")

    try:
        pid = _uuid.UUID(payment_id)
    except Exception:
        return HTTPBadRequest("invalid payment_id")

    crypto_payment = (
        request.dbsession.query(CryptoPayment).filter(CryptoPayment.id == pid).first()
    )
    if not crypto_payment:
        return HTTPBadRequest("payment not found")

    # Flash messages for status (without storing in session)
    current_status = crypto_payment.status
    if current_status == "received":
        request.session.flash(
            ("Payment received! Waiting for confirmations...", "info")
        )
    elif current_status == "confirmed":
        # Check if it's a digital product by looking at line items
        has_digital = True
        if crypto_payment.invoice:
            for line_item in crypto_payment.invoice.line_items:
                if line_item.product and line_item.product.is_physical:
                    has_digital = False
                    break

        if has_digital:
            request.session.flash(
                ("Purchase completed! Download your files now!", "success")
            )
        else:
            request.session.flash(("Purchase completed!", "success"))
    elif current_status == "confirmed-overpay":
        request.session.flash(
            ("Purchase completed! Overpayment will be refunded.", "success")
        )
    elif current_status == "expired":
        request.session.flash(("Payment quote expired.", "warning"))
    elif current_status in [
        "expired-refunded",
        "underpaid-refunded",
        "out-of-stock-refunded",
    ]:
        request.session.flash(
            ("Refund initiated. Please allow time for processing.", "info")
        )
    elif current_status == "cancelled":
        request.session.flash(("Payment cancelled.", "info"))

    payload = {
        "payment_id": str(crypto_payment.id),
        "status": crypto_payment.status,
        "address": crypto_payment.address,
        "received_amount": crypto_payment.received_amount,
        "expected_amount": crypto_payment.expected_amount,
        "confirmations_required": crypto_payment.confirmations_required,
        "current_confirmations": crypto_payment.current_confirmations or 0,
        "expires_at": crypto_payment.quote_expires_at,
    }

    # Add invoice URL for non-pending statuses
    if crypto_payment.status != "pending" and crypto_payment.invoice:
        payload["invoice_url"] = request.route_url(
            "view_invoice", invoice_id=crypto_payment.invoice.id
        )

    # Add smart redirect URL when payment is confirmed (any confirmed status)
    if (
        crypto_payment.status
        in ["confirmed", "confirmed-complete", "confirmed-overpay"]
        and crypto_payment.invoice
    ):
        from ..views.cart import get_smart_purchase_redirect_url

        redirect_url = get_smart_purchase_redirect_url([crypto_payment.invoice])
        payload["redirect_url"] = redirect_url
    return Response(
        json.dumps(payload), content_type="application/json", charset="utf-8"
    )


@view_config(route_name="crypto_doge_status")
@user_required()
def crypto_doge_status(request):
    """Get Dogecoin payment status - same logic as XMR status."""
    payment_id = request.matchdict.get("payment_id")
    if not payment_id:
        return HTTPBadRequest("missing payment_id")

    try:
        pid = _uuid.UUID(payment_id)
    except Exception:
        return HTTPBadRequest("invalid payment_id")

    crypto_payment = (
        request.dbsession.query(CryptoPayment).filter(CryptoPayment.id == pid).first()
    )
    if not crypto_payment:
        return HTTPBadRequest("payment not found")

    # Flash messages for status (without storing in session)
    current_status = crypto_payment.status
    if current_status == "received":
        request.session.flash(
            ("Payment received! Waiting for confirmations...", "info")
        )
    elif current_status == "confirmed":
        # Check if it's a digital product by looking at line items
        has_digital = True
        if crypto_payment.invoice:
            for line_item in crypto_payment.invoice.line_items:
                if line_item.product and line_item.product.is_physical:
                    has_digital = False
                    break

        if has_digital:
            request.session.flash(
                ("Purchase completed! Download your files now!", "success")
            )
        else:
            request.session.flash(("Purchase completed!", "success"))
    elif current_status == "confirmed-overpay":
        request.session.flash(
            ("Purchase completed! Overpayment will be refunded.", "success")
        )
    elif current_status == "expired":
        request.session.flash(("Payment quote expired.", "warning"))
    elif current_status in [
        "expired-refunded",
        "underpaid-refunded",
        "out-of-stock-refunded",
    ]:
        request.session.flash(
            ("Refund initiated. Please allow time for processing.", "info")
        )
    elif current_status == "cancelled":
        request.session.flash(("Payment cancelled.", "info"))

    payload = {
        "payment_id": str(crypto_payment.id),
        "status": crypto_payment.status,
        "address": crypto_payment.address,
        "received_amount": crypto_payment.received_amount,
        "expected_amount": crypto_payment.expected_amount,
        "confirmations_required": crypto_payment.confirmations_required,
        "current_confirmations": crypto_payment.current_confirmations or 0,
        "expires_at": crypto_payment.quote_expires_at,
        # Add atomic unit names for consistency with template
        "received_koinu": crypto_payment.received_amount,
        "expected_koinu": crypto_payment.expected_amount,
    }

    # Add invoice URL for non-pending statuses
    if crypto_payment.status != "pending" and crypto_payment.invoice:
        payload["invoice_url"] = request.route_url(
            "view_invoice", invoice_id=crypto_payment.invoice.id
        )

    # Add smart redirect URL when payment is confirmed (any confirmed status)
    if (
        crypto_payment.status
        in ["confirmed", "confirmed-complete", "confirmed-overpay"]
        and crypto_payment.invoice
    ):
        from ..views.cart import get_smart_purchase_redirect_url

        redirect_url = get_smart_purchase_redirect_url([crypto_payment.invoice])
        payload["redirect_url"] = redirect_url
    return Response(
        json.dumps(payload), content_type="application/json", charset="utf-8"
    )


@view_config(route_name="crypto_cancel", request_method="POST", require_csrf=True)
@user_required()
def crypto_cancel(request):
    """Cancel a pending crypto payment."""
    payment_id = request.matchdict.get("payment_id")
    if not payment_id:
        return HTTPBadRequest("missing payment_id")

    try:
        pid = _uuid.UUID(payment_id)
    except Exception:
        return HTTPBadRequest("invalid payment_id")

    crypto_payment = (
        request.dbsession.query(CryptoPayment).filter(CryptoPayment.id == pid).first()
    )
    if not crypto_payment:
        return HTTPBadRequest("payment not found")

    # Check that user owns this payment
    if crypto_payment.invoice.user_id != request.user.id:
        return HTTPBadRequest("unauthorized")

    # Only pending payments can be cancelled (before any funds are received)
    if crypto_payment.status != CryptoPayment.STATUS_PENDING:
        return HTTPBadRequest(
            f"Only pending payments can be cancelled. Current status: {crypto_payment.status}"
        )

    # Cancel the payment
    crypto_payment.status = CryptoPayment.STATUS_CANCELLED
    request.dbsession.add(crypto_payment)

    # Delete the invoice using the guarded function
    # Keep the crypto_payment for transaction history
    invoice = crypto_payment.invoice
    if invoice:
        # Clear the invoice reference BEFORE deleting the invoice (now that invoice_id is nullable)
        crypto_payment.invoice_id = None
        crypto_payment.invoice = None

        delete_result = delete_invoice_by_id(request.dbsession, invoice.id)
        # We don't fail the cancellation if invoice deletion fails
        # The payment cancellation is more important than invoice cleanup

    request.dbsession.flush()

    # Get the cart URL for redirect
    cart_url = request.route_url("cart")

    return Response(
        json.dumps(
            {"success": True, "message": "Payment cancelled", "cart_url": cart_url}
        ),
        content_type="application/json",
        charset="utf-8",
    )


@view_config(
    route_name="crypto_quotes_history",
    renderer="crypto_quotes_history.j2",
)
@user_required()
def crypto_quotes_history(request):
    """Show user's crypto payment history (all attempts, successful and failed)."""

    # Get crypto payments for this user on this shop, ordered by newest first
    # Now we can filter directly by user_id and shop_id since they're on CryptoPayment
    crypto_payments = (
        request.dbsession.query(CryptoPayment)
        .filter(
            CryptoPayment.user_id == request.user.id,
            CryptoPayment.shop_id == request.shop.id if request.shop else True,
        )
        .order_by(CryptoPayment.created_timestamp.desc())
        .all()
    )

    # Process payments for display
    payment_history = []
    for payment in crypto_payments:
        # Get coin info for display
        coin_info = get_coin_info(payment.coin_type)

        # Calculate display amounts
        amount_crypto = payment.expected_amount / coin_info["smallest_unit_divisor"]
        received_crypto = (payment.received_amount or 0) / coin_info[
            "smallest_unit_divisor"
        ]

        # Determine status display info
        status_info = get_payment_status_info(payment.status)

        # Format timestamp for display
        import datetime

        created_dt = datetime.datetime.fromtimestamp(payment.created_timestamp / 1000)
        created_formatted = created_dt.strftime("%Y-%m-%d %H:%M:%S")

        payment_data = {
            "id": str(payment.id),
            "coin_type": payment.coin_type,
            "coin_name": coin_info["name"],
            "status": payment.status,
            "status_label": status_info["label"],
            "status_color": status_info["color"],
            "amount_crypto": amount_crypto,
            "received_crypto": received_crypto,
            "usd_total": float(payment.invoice.total) if payment.invoice else 0,
            "rate_usd_per_coin": payment.rate_locked_usd_per_coin,
            "created_timestamp": payment.created_timestamp,
            "created_formatted": created_formatted,
            "quote_expires_at": payment.quote_expires_at,
            "confirmations": payment.current_confirmations or 0,
            "confirmations_required": payment.confirmations_required,
            "has_invoice": bool(payment.invoice),
            "invoice_id": payment.invoice.id if payment.invoice else None,
            "shop_name": payment.shop.name if payment.shop else "Unknown Shop",
            "refund_reason": payment.refund_reason,
            "refund_tx_hash": payment.refund_tx_hash,
        }
        payment_history.append(payment_data)

    return {
        "payments": payment_history,
        "user": request.user,
    }


def estimate_monero_fee_for_quote(settings, shop_sweep_to_address, amount_piconero):
    """Estimate Monero transaction fee for quote creation using dynamic RPC call."""
    try:
        client = get_client_from_settings(settings)

        # We need a dummy subaddress for the test - use index 0 which should exist
        # This is just for fee estimation, not actual transaction
        test_transfer_result = client._call(
            "transfer",
            {
                "destinations": [
                    {"address": shop_sweep_to_address, "amount": amount_piconero}
                ],
                "account_index": 0,  # Use account 0 for estimation
                "priority": 1,
                "do_not_relay": True,  # Don't broadcast, just estimate
                "get_tx_metadata": True,
            },
        )

        estimated_fee_piconero = math.ceil(
            test_transfer_result.get("fee", 100000000000)
        )  # Fallback to 0.0001 XMR, round UP for fees

        # Double the fee to cover both inbound (customer) and outbound (sweep) transactions
        total_fee_piconero = estimated_fee_piconero * 2

        return abs(
            Decimal(total_fee_piconero) / Decimal("1000000000000")
        )  # Convert to XMR
    except Exception as e:
        # Fallback to hardcoded fee if RPC call fails, doubled for inbound + outbound
        fallback_fee = float(settings.get("monero.fee_buffer", "0.0001")) * 2
        return abs(Decimal(str(fallback_fee)))


def estimate_dogecoin_fee_for_quote(settings):
    """Estimate Dogecoin transaction fee for quote creation using estimatesmartfee."""
    import logging

    logger = logging.getLogger(__name__)

    try:
        client = get_dogecoin_client_from_settings(settings)

        # Use estimatesmartfee to get current network fee estimate
        # Use 6 block target (~1 hour) instead of 2 blocks for cheaper fees
        fee_estimate_result = client._call("estimatesmartfee", [6])
        logger.info(f"Dogecoin estimatesmartfee result: {fee_estimate_result}")

        if fee_estimate_result and "feerate" in fee_estimate_result:
            # feerate is in DOGE per KB, estimate transaction size as ~0.15KB (realistic)
            # Typical DOGE transaction is ~150 bytes for simple transfers
            network_feerate = float(fee_estimate_result["feerate"])

            # Ensure positive feerate - negative values indicate RPC issues
            if network_feerate <= 0:
                logger.warning(
                    f"Invalid negative/zero feerate {network_feerate} from estimatesmartfee, using fallback"
                )
                raise ValueError(f"Invalid feerate: {network_feerate}")

            # Cap fee rate at reasonable maximum (100 DOGE/KB = ~$26/KB)
            # This is very generous - normal DOGE fees are much lower
            max_reasonable_feerate = 100.0
            if network_feerate > max_reasonable_feerate:
                logger.warning(
                    f"Network fee rate {network_feerate} DOGE/KB is excessive, capping at {max_reasonable_feerate} DOGE/KB"
                )
                network_feerate = max_reasonable_feerate

            estimated_fee_doge = network_feerate * 0.15
            # Add reasonable buffer for sweep transaction (not doubling)
            total_fee_doge = estimated_fee_doge * 1.5

            # Cap the total fee at a reasonable maximum (0.5 DOGE = ~$0.13)
            # This should rarely be hit if RPC is working properly
            max_reasonable_total_fee = 0.5
            if total_fee_doge > max_reasonable_total_fee:
                logger.warning(
                    f"Calculated DOGE fee {total_fee_doge} is excessive, capping at {max_reasonable_total_fee} DOGE"
                )
                total_fee_doge = max_reasonable_total_fee
            logger.info(
                f"Using dynamic DOGE fee: {network_feerate} DOGE/KB * 0.15KB * 1.5 = {total_fee_doge} DOGE"
            )
            return abs(Decimal(str(total_fee_doge)))
        else:
            # Fallback to reasonable fee if estimatesmartfee fails - RPC should be working!
            fallback_fee = float(settings.get("dogecoin.fee_buffer", "0.5"))
            logger.warning(
                f"Dogecoin estimatesmartfee failed (RPC issue?), using fallback fee: {fallback_fee} DOGE"
            )
            return abs(Decimal(str(fallback_fee)))
    except Exception as e:
        # Fallback to reasonable fee if RPC call fails - RPC should be working!
        fallback_fee = float(settings.get("dogecoin.fee_buffer", "0.5"))
        logger.error(
            f"Dogecoin fee estimation error: {e} (RPC issue?), using fallback fee: {fallback_fee} DOGE"
        )
        return abs(Decimal(str(fallback_fee)))


def get_payment_status_info(status):
    """Get display information for payment status."""
    status_mapping = {
        "pending": {"label": "Pending Payment", "color": "#ffc107"},
        "received": {"label": "Payment Received", "color": "#17a2b8"},
        "confirmed": {"label": "✓ Confirmed", "color": "#28a745"},
        "confirmed-complete": {"label": "✓ Confirmed (Complete)", "color": "#28a745"},
        "confirmed-overpay": {"label": "✓ Confirmed (Overpaid)", "color": "#28a745"},
        "confirmed-overpay-complete": {
            "label": "✓ Confirmed (Overpaid)",
            "color": "#28a745",
        },
        "expired": {"label": "Expired", "color": "#6c757d"},
        "expired": {"label": "Expired", "color": "#6c757d"},
        "latepay-refunded": {"label": "Late Payment - Refunded", "color": "#fd7e14"},
        "latepay-refunded-complete": {
            "label": "✓ Late Payment - Refunded",
            "color": "#fd7e14",
        },
        "underpaid-refunded": {"label": "Underpaid - Refunded", "color": "#fd7e14"},
        "underpaid-refunded-complete": {
            "label": "✓ Underpaid - Refunded",
            "color": "#fd7e14",
        },
        "confirmed-overpay-refunded": {
            "label": "✓ Overpaid - Refund Sent",
            "color": "#28a745",
        },
        "confirmed-overpay-refunded-complete": {
            "label": "✓ Overpaid - Refunded",
            "color": "#28a745",
        },
        "cancelled": {"label": "Cancelled", "color": "#6c757d"},
        "out-of-stock-refunded": {
            "label": "Out of Stock - Refunded",
            "color": "#fd7e14",
        },
        "out-of-stock-refunded-complete": {
            "label": "✓ Out of Stock - Refunded",
            "color": "#fd7e14",
        },
        "doublepay-refunded": {
            "label": "Duplicate Payment - Refunding",
            "color": "#fd7e14",
        },
        "doublepay-refund-complete": {
            "label": "✓ Duplicate Payment - Refunded",
            "color": "#fd7e14",
        },
        "latepay-not-refunded": {
            "label": "Late Payment - No Refund",
            "color": "#dc3545",
        },
        "underpaid-not-refunded": {
            "label": "Underpaid - No Refund",
            "color": "#dc3545",
        },
        "confirmed-overpay-not-refunded": {
            "label": "Overpaid - No Refund",
            "color": "#dc3545",
        },
        "out-of-stock-not-refunded": {
            "label": "Out of Stock - No Refund",
            "color": "#dc3545",
        },
        "doublepay-not-refunded": {
            "label": "Duplicate Payment - No Refund",
            "color": "#dc3545",
        },
    }
    return status_mapping.get(
        status.lower(), {"label": status.title(), "color": "#6c757d"}
    )


# TODO: COMMENT OUT WHEN DEBUGGING COMPLETE - TEMPORARY PRODUCTION DEBUG ROUTE
@view_config(
    route_name="crypto_debug_wallet_scan",
    request_method="GET",
    renderer="string",
)
def crypto_debug_wallet_scan(request):
    """READ-ONLY debug route to diagnose wallet scanning issue - NO SECRETS EXPOSED"""

    try:
        from ..lib.crypto_watcher import get_crypto_client
        from ..models.crypto_processor import CryptoProcessor

        settings = request.registry.settings
        db = request.dbsession

        debug_output = []
        debug_output.append("=== CRYPTO WALLET SCAN DEBUG (READ-ONLY) ===\n")

        # Check crypto processors
        processors = (
            db.query(CryptoProcessor).filter(CryptoProcessor.enabled == True).all()
        )
        debug_output.append(f"Active processors: {len(processors)}")

        for processor in processors:
            # Show processor info but mask shop IDs for security
            shop_id_masked = processor.shop_id.uuid_str[:8] + "***"
            debug_output.append(
                f"  - {processor.coin_type} processor (shop {shop_id_masked})"
            )
            debug_output.append(f"    Scan semaphore: {processor.last_scan_semaphore}")

        debug_output.append("")

        # Test XMR wallet RPC (READ-ONLY)
        if any(p.coin_type == "XMR" for p in processors):
            debug_output.append("=== TESTING XMR WALLET RPC (READ-ONLY) ===")
            try:
                client = get_crypto_client(settings, "XMR")
                debug_output.append("✓ XMR client created successfully")

                # Test the exact same call as the scanner
                query_params = {
                    "in": True,
                    "out": False,
                    "pending": True,
                    "failed": False,
                    "pool": True,
                }
                debug_output.append(f"Query params: {query_params}")

                result = client._call("get_transfers", query_params)
                debug_output.append(
                    f"RPC result keys: {list(result.keys()) if result else 'None'}"
                )

                total_transfers = 0
                for transfer_type in ["in", "pending", "pool"]:
                    if transfer_type in result:
                        transfers = result[transfer_type]
                        debug_output.append(
                            f"  {transfer_type}: {len(transfers)} transfers"
                        )
                        total_transfers += len(transfers)

                        # Show minimal transfer details (no addresses/amounts for security)
                        for i, tx in enumerate(transfers[:3]):
                            subaddr = tx.get("subaddr_index", {})
                            debug_output.append(
                                f"    Transfer {i+1}: height={tx.get('height')}, "
                                f"subaddr={subaddr.get('major', 0)}.{subaddr.get('minor')}, "
                                f"confirmations={tx.get('confirmations', 0)}"
                            )

                debug_output.append(f"Total transfers found: {total_transfers}")

            except Exception as e:
                debug_output.append(f"❌ XMR wallet RPC error: {e}")

        debug_output.append("\n=== DIAGNOSIS ===")
        debug_output.append(
            "If transfers found > 0 but scanner logs show 'No transfers', there's a bug in scanner logic"
        )
        debug_output.append(
            "If transfers found = 0, wallet has no transaction history or RPC issue"
        )
        debug_output.append("\n=== DEBUG COMPLETE ===")
        return Response("\n".join(debug_output), content_type="text/plain")
    except Exception as e:
        return Response(f"Debug error: {e}", content_type="text/plain", status=500)
