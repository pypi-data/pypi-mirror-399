# quote email address in OTP so that a plus address
# is not  decoded as a space during authentication.
try:
    # Python 2.
    from urllib import quote_plus
except ImportError:
    # Python 3.
    from urllib.parse import quote_plus

from make_post_sell.lib.mail_messages import (
    WELCOME_1_TEXT,
    WELCOME_1_HTML,
    PURCHASE_1_TEXT,
    PURCHASE_1_HTML,
    SALE_1_TEXT,
    SALE_1_HTML,
    INVITE_1_TEXT,
    INVITE_1_HTML,
)

import dkim
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Catch socket errors when postfix isn't running...
from socket import error as socket_error
import logging

log = logging.getLogger(__name__)


def send_email(
    to_email,
    sender_email,
    subject,
    message_text,
    message_html,
    relay="localhost",
    dkim_private_key_path="",
    dkim_selector="",
    dkim_signature_algorithm="ed25519-sha256",
    debug_mode=False,
):
    # The `email` library assumes it is working with string objects.
    # The `dkim` library assumes it is working with byte objects.
    # This function performs the acrobatics to make them both happy.

    if isinstance(message_text, bytes):
        # Needed for Python 3.
        message_text = message_text.decode()

    if isinstance(message_html, bytes):
        # Needed for Python 3.
        message_html = message_html.decode()

    sender_domain = sender_email.split("@")[-1]
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(message_text, "plain"))
    msg.attach(MIMEText(message_html, "html"))
    msg["To"] = to_email
    msg["From"] = sender_email
    msg["Subject"] = subject

    try:
        # Python 3 libraries expect bytes.
        msg_data = msg.as_bytes()
    except:
        # Python 2 libraries expect strings.
        msg_data = msg.as_string()

    if dkim_private_key_path and dkim_selector:
        try:
            # The dkim library uses regex on byte strings so everything
            # needs to be encoded from strings to bytes.
            with open(dkim_private_key_path) as fh:
                dkim_private_key = fh.read()
            headers = [b"To", b"From", b"Subject"]
            sig = dkim.sign(
                message=msg_data,
                selector=str(dkim_selector).encode(),
                domain=sender_domain.encode(),
                privkey=dkim_private_key.encode(),
                include_headers=headers,
                signature_algorithm=dkim_signature_algorithm.encode(),
            )
            # Add the dkim signature to the email message headers.
            # Decode the signature back to string_type because later on
            # the call to msg.as_string() performs its own bytes encoding...
            msg["DKIM-Signature"] = sig[len("DKIM-Signature: ") :].decode()

            try:
                # Python 3 libraries expect bytes.
                msg_data = msg.as_bytes()
            except AttributeError:  # For Python 2 compatibility
                # Python 2 libraries expect strings.
                msg_data = msg.as_string()
        except Exception as e:
            if debug_mode:
                log.error(f"DKIM signing failed: {str(e)}")
            raise

    try:
        s = smtplib.SMTP(relay)
        s.sendmail(sender_email, [to_email], msg_data)
        s.quit()
        return msg
    except (socket_error, smtplib.SMTPException) as e:
        error_msg = f"Failed to send email: {str(e)}"

        if debug_mode:
            # Log the error first for quick scanning
            log.error(error_msg)
            # Then log the email details
            log.info(
                f"""

Email Contents:
To: {to_email}
From: {sender_email}
Subject: {subject}

Text Content:
{message_text}

HTML Content:
{message_html}
                """
            )

        if not debug_mode:
            raise
        return None


def send_pyramid_email(request, to_email, subject, message_text, message_html):
    """Thin wrapper around `send_email` to customize settings using request object."""
    default_sender = f"no-reply@{request.domain}"
    sender_email = request.app.get("email.sender", default_sender)
    subject = f"{subject} | {request.app.get('email.subject_postfix', request.domain)}"
    relay = request.app.get("email.relay", "localhost")
    dkim_private_key_path = request.app.get("email.dkim_private_key_path", "")
    dkim_selector = request.app.get("email.dkim_selector", "")
    dkim_signature_algorithm = request.app.get(
        "email.dkim_signature_algorithm", "ed25519-sha256"
    )

    send_email(
        to_email,
        sender_email,
        subject,
        message_text,
        message_html,
        relay,
        dkim_private_key_path,
        dkim_selector,
        dkim_signature_algorithm,
        request.debug_mode,
    )


def send_verification_digits_to_email(request, to_email, raw_digits):
    """
    Send email with raw_digits a user may pass to verify & authenticate.

    request
      the request (of the successful log in attempt)

    to_email
      the email address to send the raw_digits

    raw_digits:
      the raw (unencrypted) digits the user may use to verify & authenticate.
    """
    subject = f"Verification Code | {raw_digits}"
    message_text = WELCOME_1_TEXT.format(raw_digits)
    message_html = WELCOME_1_HTML.format(subject, raw_digits)
    send_pyramid_email(request, to_email, subject, message_text, message_html)


def send_purchase_email(request, to_email, products, total_cost):
    """
    Send purchase email to customer.

    request
      the request (of the successful log in attempt)

    to_email
      the email address to send the email to.

    products
      the list of products that the customer purchased.

    total_cost
      the total transaction price.
    """
    subject = "Your purchase was successful!"
    product_text_list = []
    for p in products:
        thumbnail = ""
        if "thumbnail1" in p.extensions:
            thumbnail = '<img src="{}/{}/thumbnail1?ts={}" style="border: 1px solid #ddd; border-radius: 4px; max-width: 184px; max-height: 184px; width: auto; height: auto;" />'.format(
                request.app["bucket.secure_uploads.get_endpoint"],
                p.s3_path,
                p.updated_timestamp,
            )

        product_text_list.append(
            f'<p><a href="{p.absolute_url(request)}">{p.title}<br/>{thumbnail}</a></p>'
        )
    product_text = "<br/>".join(product_text_list)

    message_text = PURCHASE_1_TEXT.format(f"{total_cost:.2f}", request.host_url)
    message_html = PURCHASE_1_HTML.format(
        subject, request.host_url, product_text, f"{total_cost:.2f}"
    )
    send_pyramid_email(request, to_email, subject, message_text, message_html)


def send_sale_email(request, shop, products, total_cost):
    """
    Send an email to all shop owners regarding the sale.

    request
      the request (of the successful log in attempt)

    shop
      the shop that made the sale

    products
      the list of products that the customer purchased.

    total_cost
      the total transaction price.
    """
    subject = "You made a sale!"
    product_text_list = []
    for p in products:
        thumbnail = ""
        if "thumbnail1" in p.extensions:
            thumbnail = '<img src="{}/{}/thumbnail1?ts={}" style="border: 1px solid #ddd; border-radius: 4px; max-width: 184px; max-height: 184px; width: auto; height: auto;" />'.format(
                request.app["bucket.secure_uploads.get_endpoint"],
                p.s3_path,
                p.updated_timestamp,
            )

        product_text_list.append(
            f'<p><a href="{p.absolute_url(request)}">{p.title}<br/>{thumbnail}</a></p>'
        )
    product_text = "<br/>".join(product_text_list)

    message_text = SALE_1_TEXT.format(
        f"{total_cost:.2f}", shop.absolute_sales_url(request)
    )
    message_html = SALE_1_HTML.format(
        subject, shop.absolute_sales_url(request), product_text, f"{total_cost:.2f}"
    )

    # Send a separate email for each shop owner.
    for user in shop.users:
        send_pyramid_email(request, user.email, subject, message_text, message_html)


def send_no_refund_shop_notification(request, crypto_payment):
    """
    Send notification to shop owners when a payment cannot be refunded due to missing refund address.

    request
      the pyramid request

    crypto_payment
      the CryptoPayment that couldn't be refunded
    """
    if not crypto_payment.invoice or not crypto_payment.invoice.shop:
        return

    shop = crypto_payment.invoice.shop
    received_amount_crypto = crypto_payment.received_amount / (
        100_000_000 if crypto_payment.coin_type == "DOGE" else 1_000_000_000_000
    )
    customer_name = (
        crypto_payment.invoice.user.display_name
        if crypto_payment.invoice.user
        else "Unknown"
    )

    subject = f"Payment Forfeited - Funds Swept - {crypto_payment.coin_type}"

    message_text = f"""
A customer payment has been forfeited and funds swept to your account.

Payment Details:
- Amount: {received_amount_crypto} {crypto_payment.coin_type}
- Customer: {customer_name}
- Payment ID: {crypto_payment.id}

The funds were swept to you as the shop owner and forfeited by the purchaser (no valid refund address provided).
"""

    message_html = f"""
<h2>Payment Forfeited - Funds Swept</h2>

<p>A customer payment has been forfeited and funds swept to your account.</p>

<h3>Payment Details:</h3>
<ul>
<li><strong>Amount:</strong> {received_amount_crypto} {crypto_payment.coin_type}</li>
<li><strong>Customer:</strong> {customer_name}</li>
<li><strong>Payment ID:</strong> {crypto_payment.id}</li>
</ul>

<p>The funds were swept to you as the shop owner and forfeited by the purchaser (no valid refund address provided).</p>
"""

    # Send to all shop owners
    for user in shop.users:
        send_pyramid_email(request, user.email, subject, message_text, message_html)


def send_refund_email(request, to_email, crypto_payment, refund_details):
    """
    Send an email notification about a refund being processed.

    request
      the pyramid request

    to_email
      recipient email address

    crypto_payment
      the CryptoPayment object being refunded

    refund_details
      dict with refund information (amount, reason, etc)
    """
    # Import CryptoPayment to access status constants
    from ..models.crypto_payment import CryptoPayment

    refund_amount = refund_details.get("refund_amount", 0)
    fee_amount = refund_details.get("fee_amount", 0)
    received_amount = refund_details.get("received_amount", 0)
    expected_amount = refund_details.get("expected_amount", 0)
    reason = refund_details.get("reason", "")
    tx_hash = crypto_payment.refund_tx_hash or "Processing..."

    # Determine the refund type and customize messaging based on status
    has_fee = True  # Most refunds have a 9% restocking fee

    if crypto_payment.status in [
        CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
        CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
    ]:
        subject = f"Duplicate Payment Refund - {crypto_payment.coin_type}"
        explanation = "We detected a duplicate payment to an address that was already paid. Your additional payment is being refunded."

    elif crypto_payment.status in [
        CryptoPayment.STATUS_CONFIRMED_OVERPAY,
        CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED,
    ]:
        subject = f"Overpayment Refund - {crypto_payment.coin_type}"
        explanation = f"You sent {received_amount} {crypto_payment.coin_type} but only {expected_amount} {crypto_payment.coin_type} was required. The excess amount is being refunded."

    elif crypto_payment.status in [
        CryptoPayment.STATUS_LATEPAY_REFUNDED,
        CryptoPayment.STATUS_LATEPAY_REFUNDED_COMPLETE,
    ]:
        subject = f"Late Payment Refund - {crypto_payment.coin_type}"
        explanation = "Your payment was received after the quote expired. Since we cannot fulfill your order at the original rate, your payment is being refunded."

    elif crypto_payment.status in [
        CryptoPayment.STATUS_UNDERPAID_REFUNDED,
        CryptoPayment.STATUS_UNDERPAID_REFUNDED_COMPLETE,
    ]:
        subject = f"Underpayment Refund - {crypto_payment.coin_type}"
        explanation = f"You sent {received_amount} {crypto_payment.coin_type} but {expected_amount} {crypto_payment.coin_type} was required. Since the payment is insufficient, it is being refunded."

    elif crypto_payment.status in [
        CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED,
        CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE,
    ]:
        subject = f"Out of Stock Refund - {crypto_payment.coin_type}"
        explanation = "Unfortunately, one or more items in your order are out of stock. Your payment is being refunded in full."
        has_fee = False  # Out of stock refunds have NO FEE

    elif crypto_payment.status in [
        CryptoPayment.STATUS_LATEPAY_NOT_REFUNDED,
        CryptoPayment.STATUS_UNDERPAID_NOT_REFUNDED,
        CryptoPayment.STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED,
        CryptoPayment.STATUS_OUT_OF_STOCK_NOT_REFUNDED,
        CryptoPayment.STATUS_DOUBLEPAY_NOT_REFUNDED,
    ]:
        # Check if it's economically unviable vs no refund address
        if (
            crypto_payment.refund_reason
            and "economically unviable" in crypto_payment.refund_reason
        ):
            subject = f"Payment Issue - Refund Too Small - {crypto_payment.coin_type}"
            explanation = f"Your payment of {received_amount} {crypto_payment.coin_type} results in a refund amount too small to cover network transaction fees. The refund would cost more to send than its value."
        else:
            subject = f"Payment Issue - No Refund Address - {crypto_payment.coin_type}"
            explanation = "We were unable to process a refund for your payment because no refund address was configured."
        has_fee = None  # No refund means no fee message should be shown

    else:
        subject = f"Refund Initiated - {crypto_payment.coin_type}"
        explanation = reason or "Your payment is being refunded."
        has_fee = fee_amount > 0

    # Set the fee note based on whether there's a fee
    if has_fee is None:
        fee_note = ""  # No fee note for no-refund cases
    elif has_fee:
        fee_note = "A 9% restocking fee has been deducted to cover processing costs."
    else:
        fee_note = "No fees have been deducted - you will receive the full amount."

    # Build the message text based on whether there's actually a refund
    if has_fee is None:
        # No refund case - don't show refund details
        message_text = f"""{explanation}

Payment Details:
- Payment Amount: {received_amount} {crypto_payment.coin_type}
- Payment ID: {crypto_payment.id}
"""
    else:
        # Normal refund case - show refund details
        message_text = f"""{explanation}

Refund Details:
- Original Payment: {received_amount} {crypto_payment.coin_type}
- Refund Amount: {refund_amount} {crypto_payment.coin_type}
{f"- Processing Fee: {fee_amount} {crypto_payment.coin_type}" if fee_amount > 0 else ""}
- Transaction ID: {tx_hash}
- Refund Address: {crypto_payment.refund_address}

{fee_note}

Please allow up to 10 confirmations for the refund to be fully processed.
"""

    # Build the HTML message based on whether there's actually a refund
    if has_fee is None:
        # No refund case - simplified HTML
        message_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2>{subject}</h2>
    
    <p>{explanation}</p>
    
    <h3>Payment Details</h3>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 8px; font-weight: bold;">Payment Amount:</td>
            <td style="padding: 8px;">{received_amount} {crypto_payment.coin_type}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Payment ID:</td>
            <td style="padding: 8px; font-family: monospace;">{crypto_payment.id}</td>
        </tr>
    </table>
</body>
</html>
"""
    else:
        # Normal refund case - full HTML with refund details
        message_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2>{subject}</h2>
    
    <p>{explanation}</p>
    
    <h3>Refund Details</h3>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 8px; font-weight: bold;">Original Payment:</td>
            <td style="padding: 8px;">{received_amount} {crypto_payment.coin_type}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Refund Amount:</td>
            <td style="padding: 8px;">{refund_amount} {crypto_payment.coin_type}</td>
        </tr>
        {"<tr><td style='padding: 8px; font-weight: bold;'>Processing Fee:</td><td style='padding: 8px;'>" + str(fee_amount) + " " + crypto_payment.coin_type + "</td></tr>" if fee_amount > 0 else ""}
        <tr>
            <td style="padding: 8px; font-weight: bold;">Transaction ID:</td>
            <td style="padding: 8px; font-family: monospace;">{tx_hash}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Refund Address:</td>
            <td style="padding: 8px; font-family: monospace; word-break: break-all;">{crypto_payment.refund_address}</td>
        </tr>
    </table>
    
    <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
        <strong>Note:</strong> {fee_note}
    </p>
    
    <p style="color: #666; font-style: italic;">
        Please allow up to 10 confirmations for the refund to be fully processed.
    </p>
</body>
</html>
"""

    send_pyramid_email(request, to_email, subject, message_text, message_html)


def send_invite_email(request, to_email, user, shop):
    """
    Send an email to invite a user to join a shop.

    request
      the request (of the invitation)

    to_email
      the email address to send the shop invitation to.

    user
      the user who sent the invite.

    shop
      the shop the invitation is for.
    """
    subject = f"You have been invited to {shop.name}"
    join_link = request.route_url(
        "join-or-log-in",
        _query={"email": to_email},
    )
    message_text = INVITE_1_TEXT.format(user.email, shop.name, join_link)
    message_html = INVITE_1_HTML.format(subject, user.email, shop.name, join_link)
    send_pyramid_email(request, to_email, subject, message_text, message_html)
