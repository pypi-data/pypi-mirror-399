"""
Webhook handlers for payment providers.

This module handles incoming webhooks from:
- PayPal: Payment capture, order approval, disputes
- Stripe: Payment success, failure, refunds, disputes

Webhooks provide resilience when checkout flows fail after
the payment provider has successfully processed the payment.
"""
import json
import logging

from pyramid.view import view_config
from pyramid.response import Response
import requests

from ..models.invoice import get_invoice_by_paypal_order_id
from ..lib.mail import send_purchase_email, send_sale_email

log = logging.getLogger(__name__)


# =============================================================================
# PayPal Webhooks
# =============================================================================


@view_config(route_name="paypal_webhook", request_method="POST")
def paypal_webhook(request):
    """
    Handle PayPal webhook notifications.

    Key events:
    - PAYMENT.CAPTURE.COMPLETED - Payment was captured successfully
    - CHECKOUT.ORDER.APPROVED - Order approved, needs capture (backup)
    - PAYMENT.CAPTURE.DENIED - Payment was denied
    - CUSTOMER.DISPUTE.CREATED - Dispute opened

    Note: PAYMENT.CAPTURE.REFUNDED is NOT handled. Refunds are managed
    externally by PayPal and the shop owner without platform involvement.
    """
    try:
        webhook_event = json.loads(request.body.decode("utf-8"))
        event_type = webhook_event.get("event_type")
        resource = webhook_event.get("resource", {})

        log.info(f"PayPal webhook received: {event_type}")

        # Extract order ID based on event type
        order_id = _extract_order_id(event_type, resource)

        if not order_id:
            log.warning(f"PayPal webhook: Could not extract order_id from {event_type}")
            return _json_response({"status": "ok", "message": "No order_id found"}, 200)

        # Look up the invoice
        invoice = get_invoice_by_paypal_order_id(request.dbsession, order_id)
        if not invoice:
            log.warning(f"PayPal webhook: No invoice found for order {order_id}")
            return _json_response({"status": "ok", "message": "Invoice not found"}, 200)

        shop = invoice.shop
        if not shop:
            log.error(f"PayPal webhook: Invoice {invoice.id} has no shop")
            return _json_response({"status": "error", "message": "No shop"}, 400)

        # Verify webhook signature
        if not _verify_webhook_signature(request, webhook_event, shop):
            log.warning(f"PayPal webhook: Signature verification failed for order {order_id}")
            # Still return 200 to prevent PayPal from retrying endlessly
            # Log it for investigation
            return _json_response({"status": "ok", "message": "Signature verification skipped"}, 200)

        # Process the event
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            _handle_capture_completed(request, invoice, resource)

        elif event_type == "CHECKOUT.ORDER.APPROVED":
            _handle_order_approved(request, invoice, shop, order_id)

        elif event_type == "PAYMENT.CAPTURE.DENIED":
            log.warning(f"PayPal payment DENIED for order {order_id}, invoice {invoice.id}")

        elif event_type == "CUSTOMER.DISPUTE.CREATED":
            _handle_dispute_created(resource, order_id)

        return _json_response({"status": "success"}, 200)

    except Exception as e:
        log.exception(f"PayPal webhook error: {str(e)}")
        # Return 200 anyway to prevent infinite retries
        return _json_response({"status": "error", "message": str(e)}, 200)


def _extract_order_id(event_type, resource):
    """Extract order ID from webhook resource based on event type."""
    # For capture events, order_id is in supplementary_data
    if "supplementary_data" in resource:
        related_ids = resource.get("supplementary_data", {}).get("related_ids", {})
        order_id = related_ids.get("order_id")
        if order_id:
            return order_id

    # For order events, the resource itself is the order
    if event_type and "ORDER" in event_type:
        return resource.get("id")

    # Fallback: try common locations
    return resource.get("order_id") or resource.get("id")


def _verify_webhook_signature(request, webhook_event, shop):
    """
    Verify PayPal webhook signature.

    Returns True if verified, False if verification failed or skipped.
    """
    # Get webhook ID from app settings (configured per-deployment)
    webhook_id = request.registry.settings.get("paypal.webhook_id")
    if not webhook_id:
        log.debug("PayPal webhook_id not configured, skipping verification")
        return True  # Skip verification if not configured

    # Get required headers
    headers = {
        "transmission_id": request.headers.get("PAYPAL-TRANSMISSION-ID"),
        "transmission_time": request.headers.get("PAYPAL-TRANSMISSION-TIME"),
        "cert_url": request.headers.get("PAYPAL-CERT-URL"),
        "auth_algo": request.headers.get("PAYPAL-AUTH-ALGO"),
        "transmission_sig": request.headers.get("PAYPAL-TRANSMISSION-SIG"),
    }

    if not all(headers.values()):
        log.warning("PayPal webhook: Missing verification headers")
        return False

    try:
        # Determine API base URL
        sandbox_mode = request.registry.settings.get("app.paypal.sandbox_mode", "True")
        is_sandbox = str(sandbox_mode).lower() in ("true", "1", "yes")
        base_url = "https://api-m.sandbox.paypal.com" if is_sandbox else "https://api-m.paypal.com"

        # Get OAuth token
        auth_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
            auth=(shop.paypal_client_id, shop.paypal_secret),
            timeout=10
        )

        if auth_response.status_code != 200:
            log.error(f"PayPal webhook auth failed: {auth_response.text}")
            return False

        access_token = auth_response.json()["access_token"]

        # Verify signature
        verify_response = requests.post(
            f"{base_url}/v1/notifications/verify-webhook-signature",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json={
                "transmission_id": headers["transmission_id"],
                "transmission_time": headers["transmission_time"],
                "cert_url": headers["cert_url"],
                "auth_algo": headers["auth_algo"],
                "transmission_sig": headers["transmission_sig"],
                "webhook_id": webhook_id,
                "webhook_event": webhook_event
            },
            timeout=10
        )

        if verify_response.status_code != 200:
            log.error(f"PayPal webhook verification API error: {verify_response.text}")
            return False

        result = verify_response.json()
        if result.get("verification_status") == "SUCCESS":
            log.debug("PayPal webhook signature verified")
            return True
        else:
            log.warning(f"PayPal webhook signature invalid: {result}")
            return False

    except Exception as e:
        log.exception(f"PayPal webhook verification error: {e}")
        return False


def _handle_capture_completed(request, invoice, resource):
    """
    Handle PAYMENT.CAPTURE.COMPLETED event.

    This is the backup for when the JS callback fails but PayPal
    successfully captured the payment.
    """
    capture_id = resource.get("id")

    # Idempotency: check if already processed
    if invoice.paypal_capture_id:
        log.info(f"PayPal webhook: Invoice {invoice.id} already has capture_id, skipping")
        return

    log.info(f"PayPal webhook: Processing capture {capture_id} for invoice {invoice.id}")

    # Update invoice with capture ID
    invoice.paypal_capture_id = capture_id
    request.dbsession.add(invoice)

    # Unlock products for the user
    user = invoice.user
    if user:
        for line_item in invoice.line_items:
            if not line_item.product.is_unlocked_for_user(user):
                line_item.product.unlock_for_user(user)
                request.dbsession.add(line_item.product)
                log.info(f"PayPal webhook: Unlocked product {line_item.product.id} for user {user.id}")

        # Send confirmation emails
        try:
            products = [item.product for item in invoice.line_items]
            send_purchase_email(request, user.email, products, invoice.total)
            send_sale_email(request, invoice.shop, products, invoice.total)
            log.info(f"PayPal webhook: Sent confirmation emails for invoice {invoice.id}")
        except Exception as e:
            log.exception(f"PayPal webhook: Failed to send emails for invoice {invoice.id}: {e}")

    request.dbsession.flush()


def _handle_order_approved(request, invoice, shop, order_id):
    """
    Handle CHECKOUT.ORDER.APPROVED event.

    This means the customer approved the payment in PayPal, but we haven't
    captured it yet. This is a backup in case our JS onApprove failed.
    """
    # Check if already captured
    if invoice.paypal_capture_id:
        log.info(f"PayPal webhook: Order {order_id} already captured, skipping")
        return

    log.info(f"PayPal webhook: Order {order_id} approved but not captured, attempting capture")

    try:
        # Determine API base URL
        sandbox_mode = request.registry.settings.get("app.paypal.sandbox_mode", "True")
        is_sandbox = str(sandbox_mode).lower() in ("true", "1", "yes")
        base_url = "https://api-m.sandbox.paypal.com" if is_sandbox else "https://api-m.paypal.com"

        # Get OAuth token
        auth_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
            auth=(shop.paypal_client_id, shop.paypal_secret),
            timeout=10
        )

        if auth_response.status_code != 200:
            log.error(f"PayPal webhook: Auth failed for capture attempt: {auth_response.text}")
            return

        access_token = auth_response.json()["access_token"]

        # Capture the payment
        capture_response = requests.post(
            f"{base_url}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            timeout=15
        )

        if capture_response.status_code not in [200, 201]:
            log.error(f"PayPal webhook: Capture failed for order {order_id}: {capture_response.text}")
            return

        order = capture_response.json()
        log.info(f"PayPal webhook: Successfully captured order {order_id}")

        # Extract capture ID
        try:
            capture_id = order["purchase_units"][0]["payments"]["captures"][0]["id"]
            invoice.paypal_capture_id = capture_id
            request.dbsession.add(invoice)
        except (KeyError, IndexError):
            log.warning(f"PayPal webhook: Could not extract capture_id from response")

        # Unlock products and send emails
        user = invoice.user
        if user:
            for line_item in invoice.line_items:
                if not line_item.product.is_unlocked_for_user(user):
                    line_item.product.unlock_for_user(user)
                    request.dbsession.add(line_item.product)

            try:
                products = [item.product for item in invoice.line_items]
                send_purchase_email(request, user.email, products, invoice.total)
                send_sale_email(request, invoice.shop, products, invoice.total)
                log.info(f"PayPal webhook: Sent emails after webhook-initiated capture")
            except Exception as e:
                log.exception(f"PayPal webhook: Failed to send emails: {e}")

        request.dbsession.flush()

    except Exception as e:
        log.exception(f"PayPal webhook: Error capturing order {order_id}: {e}")


def _handle_dispute_created(resource, order_id):
    """Handle CUSTOMER.DISPUTE.CREATED event."""
    dispute_id = resource.get("dispute_id", "unknown")
    dispute_amount = resource.get("dispute_amount", {}).get("value", "unknown")
    dispute_reason = resource.get("reason", "unknown")

    log.critical(
        f"PayPal DISPUTE created - Order: {order_id}, "
        f"Dispute ID: {dispute_id}, Amount: ${dispute_amount}, Reason: {dispute_reason}"
    )


def _json_response(data, status):
    """Create a JSON response."""
    return Response(
        json.dumps(data),
        content_type="application/json; charset=utf-8",
        status=status
    )


# =============================================================================
# Stripe Webhooks
# =============================================================================


@view_config(route_name="stripe_webhook", request_method="POST")
def stripe_webhook(request):
    """
    Handle Stripe webhook notifications.

    Key events:
    - payment_intent.succeeded - Payment completed successfully
    - payment_intent.payment_failed - Payment failed
    - charge.refunded - Refund processed
    - charge.dispute.created - Dispute opened

    This provides resilience when the checkout flow fails after Stripe
    has successfully processed the payment.
    """
    import stripe

    try:
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")

        # Get webhook secret from settings
        webhook_secret = request.registry.settings.get("stripe.webhook_secret")

        if webhook_secret and sig_header:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError:
                log.warning("Stripe webhook: Invalid payload")
                return _json_response({"error": "Invalid payload"}, 400)
            except stripe.error.SignatureVerificationError:
                log.warning("Stripe webhook: Invalid signature")
                return _json_response({"error": "Invalid signature"}, 400)
        else:
            # No webhook secret configured, parse without verification
            event = json.loads(payload.decode("utf-8"))
            log.debug("Stripe webhook: No webhook_secret configured, skipping verification")

        event_type = event.get("type") if isinstance(event, dict) else event.type
        data_object = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object

        log.info(f"Stripe webhook received: {event_type}")

        if event_type == "payment_intent.succeeded":
            _handle_stripe_payment_succeeded(request, data_object)

        elif event_type == "payment_intent.payment_failed":
            _handle_stripe_payment_failed(request, data_object)

        elif event_type == "charge.refunded":
            _handle_stripe_refund(request, data_object)

        elif event_type == "charge.dispute.created":
            _handle_stripe_dispute(request, data_object)

        return _json_response({"status": "success"}, 200)

    except Exception as e:
        log.exception(f"Stripe webhook error: {str(e)}")
        return _json_response({"status": "error", "message": str(e)}, 200)


def _handle_stripe_payment_succeeded(request, payment_intent):
    """
    Handle payment_intent.succeeded event.

    This is the backup for when our checkout flow fails after Stripe
    has successfully charged the card.
    """
    from ..models.invoice import get_invoice_by_stripe_payment_intent_id

    payment_intent_id = payment_intent.get("id") if isinstance(payment_intent, dict) else payment_intent.id

    invoice = get_invoice_by_stripe_payment_intent_id(request.dbsession, payment_intent_id)

    if not invoice:
        log.warning(f"Stripe webhook: No invoice found for payment_intent {payment_intent_id}")
        return

    # Check if already processed (has charge_id)
    if invoice.stripe_charge_id:
        log.info(f"Stripe webhook: Invoice {invoice.id} already processed, skipping")
        return

    log.info(f"Stripe webhook: Processing payment_intent {payment_intent_id} for invoice {invoice.id}")

    # Update invoice with charge ID
    latest_charge = payment_intent.get("latest_charge") if isinstance(payment_intent, dict) else payment_intent.latest_charge
    if latest_charge:
        invoice.stripe_charge_id = latest_charge
        request.dbsession.add(invoice)

    # Unlock products for the user
    user = invoice.user
    if user:
        for line_item in invoice.line_items:
            if not line_item.product.is_unlocked_for_user(user):
                line_item.product.unlock_for_user(user)
                request.dbsession.add(line_item.product)
                log.info(f"Stripe webhook: Unlocked product {line_item.product.id} for user {user.id}")

        # Send confirmation emails
        try:
            products = [item.product for item in invoice.line_items]
            send_purchase_email(request, user.email, products, invoice.total)
            send_sale_email(request, invoice.shop, products, invoice.total)
            log.info(f"Stripe webhook: Sent confirmation emails for invoice {invoice.id}")
        except Exception as e:
            log.exception(f"Stripe webhook: Failed to send emails for invoice {invoice.id}: {e}")

    request.dbsession.flush()


def _handle_stripe_payment_failed(request, payment_intent):
    """Handle payment_intent.payment_failed event."""
    payment_intent_id = payment_intent.get("id") if isinstance(payment_intent, dict) else payment_intent.id
    error_message = ""

    if isinstance(payment_intent, dict):
        last_error = payment_intent.get("last_payment_error", {})
        error_message = last_error.get("message", "Unknown error")
    else:
        if payment_intent.last_payment_error:
            error_message = payment_intent.last_payment_error.message or "Unknown error"

    log.warning(f"Stripe payment FAILED for payment_intent {payment_intent_id}: {error_message}")


def _handle_stripe_refund(request, charge):
    """Handle charge.refunded event."""
    charge_id = charge.get("id") if isinstance(charge, dict) else charge.id
    amount_refunded = charge.get("amount_refunded", 0) if isinstance(charge, dict) else charge.amount_refunded

    # Convert from cents to dollars
    amount_dollars = amount_refunded / 100

    log.info(f"Stripe REFUND processed - Charge: {charge_id}, Amount: ${amount_dollars:.2f}")


def _handle_stripe_dispute(request, dispute):
    """Handle charge.dispute.created event."""
    dispute_id = dispute.get("id") if isinstance(dispute, dict) else dispute.id
    charge_id = dispute.get("charge") if isinstance(dispute, dict) else dispute.charge
    amount = dispute.get("amount", 0) if isinstance(dispute, dict) else dispute.amount
    reason = dispute.get("reason", "unknown") if isinstance(dispute, dict) else dispute.reason

    # Convert from cents to dollars
    amount_dollars = amount / 100

    log.critical(
        f"Stripe DISPUTE created - Dispute ID: {dispute_id}, "
        f"Charge: {charge_id}, Amount: ${amount_dollars:.2f}, Reason: {reason}"
    )


# =============================================================================
# Adyen Webhooks
# =============================================================================


@view_config(route_name="adyen_webhook", request_method="POST")
def adyen_webhook(request):
    """
    Handle Adyen webhook notifications.

    Key events:
    - AUTHORISATION - Payment authorized
    - CAPTURE - Payment captured
    - REFUND - Refund processed
    - CHARGEBACK - Dispute/chargeback created

    Adyen uses HMAC-SHA256 for webhook verification.
    """
    import hashlib
    import hmac
    import base64
    import binascii

    try:
        payload = request.body.decode("utf-8")
        notification = json.loads(payload)

        # Adyen sends notifications in a wrapper
        notification_items = notification.get("notificationItems", [])

        for item in notification_items:
            notification_request = item.get("NotificationRequestItem", {})
            event_code = notification_request.get("eventCode")
            psp_reference = notification_request.get("pspReference")
            merchant_reference = notification_request.get("merchantReference")

            log.info(f"Adyen webhook received: {event_code} for PSP ref {psp_reference}")

            # Find the invoice by PSP reference
            from ..models.invoice import get_invoice_by_adyen_psp_reference

            invoice = get_invoice_by_adyen_psp_reference(request.dbsession, psp_reference)

            if not invoice:
                # Try to find by merchant reference (which includes cart/shop info)
                log.info(f"Adyen webhook: No invoice found for PSP ref {psp_reference}, trying merchant ref")
                # We can't verify the signature without the shop, so just acknowledge
                continue

            shop = invoice.shop
            if not shop:
                log.error(f"Adyen webhook: Invoice {invoice.id} has no shop")
                continue

            # Verify HMAC signature
            if shop.adyen_hmac_key:
                hmac_signature = request.headers.get("X-Adyen-Hmac-Signature")
                if hmac_signature:
                    if not _verify_adyen_hmac(shop.adyen_hmac_key, hmac_signature, notification_request):
                        log.warning(f"Adyen webhook: HMAC verification failed for PSP ref {psp_reference}")
                        continue

            # Process the event
            if event_code == "AUTHORISATION":
                success = notification_request.get("success") == "true"
                if success:
                    _handle_adyen_authorisation(request, invoice, notification_request)
                else:
                    reason = notification_request.get("reason", "Unknown")
                    log.warning(f"Adyen AUTHORISATION failed for PSP ref {psp_reference}: {reason}")

            elif event_code == "CAPTURE":
                _handle_adyen_capture(request, invoice, notification_request)

            elif event_code == "REFUND":
                _handle_adyen_refund(notification_request, psp_reference)

            elif event_code == "CHARGEBACK":
                _handle_adyen_chargeback(notification_request, psp_reference)

        # Adyen expects [accepted] as response
        return Response("[accepted]", content_type="text/plain; charset=utf-8", status=200)

    except Exception as e:
        log.exception(f"Adyen webhook error: {str(e)}")
        # Return accepted to prevent infinite retries
        return Response("[accepted]", content_type="text/plain; charset=utf-8", status=200)


def _verify_adyen_hmac(hmac_key, hmac_signature, notification_request):
    """
    Verify Adyen webhook HMAC signature.

    Adyen's HMAC is computed from a specific concatenation of fields.
    """
    import hashlib
    import hmac
    import base64
    import binascii

    try:
        # Build the signing string according to Adyen's specification
        # Fields: pspReference, originalReference, merchantAccountCode, merchantReference,
        #         amount.value, amount.currency, eventCode, success
        psp_reference = notification_request.get("pspReference", "")
        original_reference = notification_request.get("originalReference", "")
        merchant_account = notification_request.get("merchantAccountCode", "")
        merchant_reference = notification_request.get("merchantReference", "")
        amount = notification_request.get("amount", {})
        amount_value = str(amount.get("value", ""))
        amount_currency = amount.get("currency", "")
        event_code = notification_request.get("eventCode", "")
        success = notification_request.get("success", "")

        # Concatenate with colons
        signing_string = ":".join([
            psp_reference,
            original_reference,
            merchant_account,
            merchant_reference,
            amount_value,
            amount_currency,
            event_code,
            success
        ])

        # Compute HMAC-SHA256
        expected = hmac.new(
            binascii.unhexlify(hmac_key),
            signing_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(expected).decode('utf-8')

        return hmac.compare_digest(hmac_signature, expected_signature)

    except Exception as e:
        log.exception(f"Adyen HMAC verification error: {e}")
        return False


def _handle_adyen_authorisation(request, invoice, notification):
    """
    Handle AUTHORISATION event.

    This confirms the payment was authorized successfully.
    """
    psp_reference = notification.get("pspReference")

    # Idempotency check
    if invoice.adyen_psp_reference == psp_reference:
        log.info(f"Adyen webhook: Invoice {invoice.id} already has PSP ref, checking products")

    # Update invoice if needed
    if not invoice.adyen_psp_reference:
        invoice.adyen_psp_reference = psp_reference
        request.dbsession.add(invoice)

    # Unlock products for the user
    user = invoice.user
    if user:
        for line_item in invoice.line_items:
            if not line_item.product.is_unlocked_for_user(user):
                line_item.product.unlock_for_user(user)
                request.dbsession.add(line_item.product)
                log.info(f"Adyen webhook: Unlocked product {line_item.product.id} for user {user.id}")

        # Send confirmation emails
        try:
            products = [item.product for item in invoice.line_items]
            send_purchase_email(request, user.email, products, invoice.total)
            send_sale_email(request, invoice.shop, products, invoice.total)
            log.info(f"Adyen webhook: Sent confirmation emails for invoice {invoice.id}")
        except Exception as e:
            log.exception(f"Adyen webhook: Failed to send emails for invoice {invoice.id}: {e}")

    request.dbsession.flush()


def _handle_adyen_capture(request, invoice, notification):
    """Handle CAPTURE event - payment was captured."""
    psp_reference = notification.get("pspReference")
    log.info(f"Adyen CAPTURE processed for invoice {invoice.id}, PSP ref {psp_reference}")


def _handle_adyen_refund(notification, psp_reference):
    """Handle REFUND event."""
    amount = notification.get("amount", {})
    amount_value = amount.get("value", 0)
    currency = amount.get("currency", "USD")

    # Convert from minor units
    amount_dollars = amount_value / 100

    log.info(f"Adyen REFUND processed - PSP ref: {psp_reference}, Amount: {amount_dollars:.2f} {currency}")


def _handle_adyen_chargeback(notification, psp_reference):
    """Handle CHARGEBACK event."""
    amount = notification.get("amount", {})
    amount_value = amount.get("value", 0)
    currency = amount.get("currency", "USD")
    reason = notification.get("reason", "unknown")

    # Convert from minor units
    amount_dollars = amount_value / 100

    log.critical(
        f"Adyen CHARGEBACK created - PSP ref: {psp_reference}, "
        f"Amount: {amount_dollars:.2f} {currency}, Reason: {reason}"
    )
