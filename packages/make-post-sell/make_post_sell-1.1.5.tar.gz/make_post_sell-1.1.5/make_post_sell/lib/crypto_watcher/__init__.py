import argparse
import json
import sys
import time
import logging
import uuid
from typing import List
from decimal import Decimal
from urllib.parse import urlparse

import sqlalchemy as sa
from pyramid.paster import bootstrap, setup_logging

from .crypto_clients import get_client_from_settings, get_dogecoin_client_from_settings
from ...models.crypto_payment import CryptoPayment
from ...models.crypto_processor import CryptoProcessor
from ...models.invoice import Invoice, delete_invoice_by_id
from ..mail import (
    send_purchase_email,
    send_sale_email,
    send_refund_email,
    send_no_refund_shop_notification,
)
from ...models.inventory import get_inventory_by_product_and_shop_location
from .crypto_payment_rescue import PaymentRescue
from ...models.meta import now_timestamp
from ...models.user_crypto_refund_address import UserCryptoRefundAddress

logger = logging.getLogger(__name__)

# Global confirmation requirements for outbound transactions (sweeps and refunds)
# These apply AFTER the payment is already confirmed incoming
OUTBOUND_CONFIRMATIONS_REQUIRED = {
    "XMR": 10,  # Monero: 10 confirmations for both sweeps and refunds
    "DOGE": 2,  # Dogecoin: 2 confirmations for both sweeps and refunds
}


class CryptoWatcherLogger:
    """Centralized logging helper for crypto watcher operations."""

    def __init__(self, logger_instance=None):
        self.logger = logger_instance or logger

    def payment_info(self, payment, message: str, **kwargs):
        """Log payment-related info with standardized format."""
        context = f" {kwargs.get('context', '')}" if kwargs.get("context") else ""
        self.logger.info(f"{message}: {payment}{context}")

    def payment_warning(self, payment, message: str, **kwargs):
        """Log payment-related warning with standardized format."""
        context = f" {kwargs.get('context', '')}" if kwargs.get("context") else ""
        self.logger.warning(f"{message}: {payment}{context}")

    def payment_error(self, payment, message: str, error=None, **kwargs):
        """Log payment-related error with standardized format."""
        context = f" {kwargs.get('context', '')}" if kwargs.get("context") else ""
        error_detail = f" - {error}" if error else ""
        self.logger.error(f"{message}: {payment}{context}{error_detail}")

    def payment_debug(self, payment, message: str, **kwargs):
        """Log payment-related debug with standardized format."""
        context = f" {kwargs.get('context', '')}" if kwargs.get("context") else ""
        self.logger.debug(f"{message}: {payment}{context}")

    def transaction_processing(
        self, payment, action: str, tx_hash: str = None, amount: int = None
    ):
        """Log transaction processing events."""
        tx_info = f" tx:{tx_hash[:16]}..." if tx_hash else ""
        amount_info = f" amount:{amount}" if amount is not None else ""
        self.logger.info(f"{action}: {payment}{tx_info}{amount_info}")

    def state_transition(
        self, payment, old_status: str, new_status: str, reason: str = ""
    ):
        """Log state transitions with context."""
        reason_info = f" ({reason})" if reason else ""
        self.logger.info(
            f"State transition: {payment} {old_status} → {new_status}{reason_info}"
        )

    def refund_operation(
        self, payment, operation: str, tx_hash: str = None, amount: int = None
    ):
        """Log refund operations."""
        tx_info = f" tx:{tx_hash[:16]}..." if tx_hash else ""
        amount_info = f" amount:{amount}" if amount is not None else ""
        self.logger.info(f"Refund {operation}: {payment}{tx_info}{amount_info}")

    def sweep_operation(
        self, payment, operation: str, tx_hash: str = None, amount: int = None
    ):
        """Log sweep operations."""
        tx_info = f" tx:{tx_hash[:16]}..." if tx_hash else ""
        amount_info = f" amount:{amount}" if amount is not None else ""
        self.logger.info(f"Sweep {operation}: {payment}{tx_info}{amount_info}")

    def confirmation_update(self, payment, old_count: int, new_count: int):
        """Log confirmation count updates."""
        self.logger.info(f"Confirmations updated: {payment} {old_count} → {new_count}")

    def processing_cycle(
        self, message: str, payment_count: int = None, cycle_info: str = ""
    ):
        """Log processing cycle information."""
        count_info = f" ({payment_count} payments)" if payment_count is not None else ""
        cycle_detail = f" {cycle_info}" if cycle_info else ""
        self.logger.info(f"Processing cycle: {message}{count_info}{cycle_detail}")

    def error_with_context(self, message: str, error, payment=None, context: str = ""):
        """Log errors with payment context when available."""
        payment_info = f" {payment}" if payment else ""
        context_info = f" ({context})" if context else ""
        self.logger.error(f"{message}{payment_info}{context_info} - {error}")


# Create logger instance for module use
log = CryptoWatcherLogger()


def _get_user_refund_address(dbsession, user_id, coin_type):
    """Get user's saved refund address for the given coin type."""
    if not user_id:
        return None

    refund_address = (
        dbsession.query(UserCryptoRefundAddress)
        .filter(
            UserCryptoRefundAddress.user_id == user_id,
            UserCryptoRefundAddress.coin_type == coin_type,
        )
        .first()
    )

    if refund_address:
        return refund_address.address
    return None


def _get_scan_position_from_semaphore(semaphore, coin_type):
    """Extract scan position from semaphore string.

    Args:
        semaphore: String in format "type:value" or None
        coin_type: Coin type for context

    Returns:
        int: Scan position (height for XMR, 0 if no semaphore)
    """
    if not semaphore:
        return 0

    if ":" not in semaphore:
        return 0

    sem_type, value = semaphore.split(":", 1)

    if coin_type == "XMR" and sem_type == "height":
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    elif coin_type in ("DOGE", "BTC", "LTC", "BCH") and sem_type == "blockhash":
        # For blockhash semaphores, we can't directly compare
        # Return 1 to indicate we have a valid starting point
        return 1 if value else 0

    return 0


def _format_scan_semaphore(coin_type, position_value):
    """Format scan position into semaphore string.

    Args:
        coin_type: Coin type
        position_value: Position value (height for XMR, blockhash for DOGE/BTC)

    Returns:
        str: Formatted semaphore string
    """
    if coin_type == "XMR":
        return f"height:{position_value}"
    elif coin_type in ("DOGE", "BTC", "LTC", "BCH"):
        return f"blockhash:{position_value}"

    return None


def _create_duplicate_payment(original_payment, tx, coin_type, dbsession=None):
    """
    Create a new payment object for a duplicate transaction.

    This allows tracking each duplicate payment separately with its own
    refund transaction and status transitions. Each unique transaction ID
    gets its own duplicate payment record, enabling proper handling of
    multiple payments (double-pay, triple-pay, etc.) to the same address.

    Args:
        original_payment: The original CryptoPayment that received the first payment
        tx: Transaction data from the blockchain client (contains txid and amount)
        coin_type: Cryptocurrency type ("XMR", "DOGE", "BTC")
        dbsession: Database session for looking up user refund addresses

    Returns:
        CryptoPayment: New duplicate payment record with STATUS_DOUBLEPAY_REFUNDED

    Note:
        - For DOGE/BTC: tx.amount is already in atomic units from get_dogecoin_incoming_transfers
        - For XMR: tx.amount is in atomic units (piconero) from monero-wallet-rpc
        - Each duplicate gets a unique ID and can be refunded independently
    """

    # Define local get_coin_config for this function
    def get_coin_config(coin_type):
        configs = {
            "XMR": {"atomic_units": 1e12},
            "DOGE": {"atomic_units": 1e8},
            "BTC": {"atomic_units": 1e8},
        }
        return configs.get(coin_type, {"atomic_units": 1e12})

    # Get coin configuration for amount conversion
    coin_config = get_coin_config(coin_type)
    atomic_units = coin_config["atomic_units"]

    # Convert transaction amount to atomic units
    if coin_type == "XMR":
        tx_amount = int(tx.get("amount", 0))
    elif coin_type == "DOGE":
        # DOGE amount from get_dogecoin_incoming_transfers is already in atomic units (koinu)
        tx_amount = int(tx.get("amount", 0))
    else:
        # BTC and others - convert from BTC to satoshi
        tx_amount = int(float(tx.get("amount", 0)) * 1e8)

    # Determine refund address - use original payment's or lookup user's saved address
    refund_address = original_payment.refund_address
    if not refund_address and dbsession and original_payment.user_id:
        refund_address = _get_user_refund_address(
            dbsession, original_payment.user_id, coin_type
        )
        if refund_address:
            log.payment_info(
                original_payment,
                f"Using saved refund address: {refund_address[:16]}...",
            )

    # Create new payment object for this duplicate using proper constructor
    duplicate_payment = CryptoPayment(
        invoice=original_payment.invoice,  # Same invoice - they're all payments toward the same order
        user=original_payment.user,
        shop=original_payment.shop,
        address=original_payment.address,
        account_index=original_payment.account_index,
        subaddress_index=original_payment.subaddress_index,
        coin_type=original_payment.coin_type,
        expected_amount=tx_amount,  # What we "expected" (the duplicate amount)
        rate_locked_usd_per_coin=original_payment.rate_locked_usd_per_coin,
        quote_expires_at_ms=int(
            time.time() * 1000
        ),  # Already "expired" since it's a duplicate
        confirmations_required=original_payment.confirmations_required,
        shop_location=original_payment.shop_location,
        shop_sweep_to_address=original_payment.shop_sweep_to_address,
        refund_address=refund_address,
    )

    # Explicitly set user_id and shop_id to ensure foreign key constraints are satisfied
    duplicate_payment.user_id = original_payment.user_id
    duplicate_payment.shop_id = original_payment.shop_id

    # Override specific properties for duplicate
    duplicate_payment.received_amount = tx_amount  # What we received
    duplicate_payment.status = CryptoPayment.STATUS_DOUBLEPAY_REFUNDED
    duplicate_payment.current_confirmations = tx.get("confirmations", 0)

    # Store the transaction ID so scanner can find this duplicate
    txid = tx.get("txid") or tx.get("transaction_id")
    if txid:
        duplicate_payment.tx_hashes = json.dumps([txid])

    return duplicate_payment


def _should_process_late_payment(payment, tx):
    """Check if a payment should be processed as a late/edge case payment.

    Handles all edge cases:
    1. Late payment to expired quote
    2. Late payment to cancelled quote
    3. Double payment to completed order
    4. Overpayment
    5. Multiple payments to same quote
    6. Underpayment top-up

    Args:
        payment: CryptoPayment object
        tx: Transaction data

    Returns:
        bool: True if this payment should be processed
    """
    if not payment:
        log.processing_cycle("_should_process_late_payment: No payment object")
        return False

    # Get transaction amount (normalize for coin type)
    if payment.coin_type == "XMR":
        tx_amount = int(tx.get("amount", 0))
    else:
        # DOGE/BTC amount is already in atomic units
        tx_amount = int(float(tx.get("amount", 0)) * 1e8)

    log.payment_debug(payment, f"Late payment check - tx_amount={tx_amount}")

    # Edge Case: Any payment with non-pending status means invalid multiple payment
    # ALL multiple payments are invalid - no legitimate double payments exist
    if payment.status != CryptoPayment.STATUS_PENDING and tx_amount > 0:
        current_total = payment.received_amount + tx_amount
        log.payment_warning(
            payment,
            f"Invalid multiple payment detected - new {tx_amount}, total {current_total}",
        )

        # Log specific scenarios for clarity
        if payment.status in [
            CryptoPayment.STATUS_EXPIRED,
            CryptoPayment.STATUS_CANCELLED,
        ]:
            log.payment_info(
                payment, "Late payment detected", context="expired/cancelled quote"
            )
        elif payment.status in [
            CryptoPayment.STATUS_CONFIRMED,
            CryptoPayment.STATUS_CONFIRMED_OVERPAY,
            CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED,
            CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE,
        ]:
            log.payment_info(
                payment, "Double payment detected", context="completed order"
            )
        elif current_total > payment.expected_amount:
            log.payment_info(
                payment,
                f"Overpayment detected",
                context=f"expected {payment.expected_amount}, receiving {current_total}",
            )
        else:
            log.payment_warning(
                payment, "Invalid multiple payment detected", context="unknown scenario"
            )

        log.payment_info(
            payment, "Accepting non-pending payment", context="late payment processing"
        )
        return True

    # Edge Case: First payment to a fresh quote (normal processing should handle this, but just in case)
    if payment.received_amount == 0 and payment.status == CryptoPayment.STATUS_PENDING:
        log.payment_info(payment, "Accepting first payment to fresh quote")
        return True

    log.payment_info(
        payment,
        f"Rejecting late payment - tx_amount={tx_amount}",
        context="validation failed",
    )
    return False


# Constants
COIN_CONFIGS = {
    "XMR": {
        "atomic_units": Decimal("1000000000000"),  # 1 XMR = 10^12 piconero
        "min_sweep_balance": Decimal("0.001"),  # Keep minimal 0.001 XMR for fees
        "confirmations_required": 2,  # XMR confirmations
    },
    "DOGE": {
        "atomic_units": Decimal("100000000"),  # 1 DOGE = 10^8 koinu
        "min_sweep_balance": Decimal("0.1"),  # Keep minimal 0.1 DOGE for fees
        "confirmations_required": 2,  # DOGE confirmations (not 10)
    },
}


def delete_invoice_for_terminal_state(dbsession, crypto_payment):
    """
    Delete invoices for failed payments, keep invoices for successful payments.

    Business Logic:
    - Successful payments: Customer received product -> Keep invoice
    - Failed payments: Customer did not receive product -> Delete invoice
    """
    # Skip if no invoice
    if not crypto_payment.invoice:
        return

    # Use semantic helper method for clean business logic
    if crypto_payment.should_keep_invoice():
        return

    # Delete invoice for all other terminal states
    invoice = crypto_payment.invoice
    log.payment_info(
        crypto_payment, f"Deleting invoice {invoice.id}", context="terminal payment"
    )

    # Delete the invoice first, then clear the reference
    try:
        delete_result = delete_invoice_by_id(dbsession, invoice.id)
        if delete_result.get("success", False):
            log.payment_info(
                crypto_payment,
                f"Successfully deleted invoice {invoice.id}: {delete_result.get('message', '')}",
            )
            # Only clear the reference after successful deletion
            crypto_payment.invoice_id = None
            crypto_payment.invoice = None
            dbsession.add(crypto_payment)
        else:
            log.error_with_context(
                f"Failed to delete invoice {invoice.id}",
                delete_result.get("message", "Unknown error"),
            )
    except Exception as e:
        log.error_with_context(f"Error deleting invoice {invoice.id}", e)


def get_crypto_client(settings, coin_type):
    """Get the appropriate crypto client for the given coin type."""
    if coin_type == "XMR":
        return get_client_from_settings(settings)
    elif coin_type == "DOGE":
        return get_dogecoin_client_from_settings(settings)
    else:
        raise ValueError(f"Unsupported coin type: {coin_type}")


def get_coin_config(coin_type):
    """Get configuration for a specific coin type."""
    return COIN_CONFIGS.get(coin_type, COIN_CONFIGS["XMR"])


def sweep_restocking_fee(settings, payment, refund_details, dbsession, context=""):
    """
    Sweep the restocking fee to the shop owner's address after a refund.

    Args:
        settings: Pyramid settings
        payment: CryptoPayment object
        refund_details: Dict with refund details including fee_amount
        dbsession: Database session
        context: String describing the refund context (for logging)
    """
    import logging
    import time
    from decimal import Decimal

    if not payment.shop_sweep_to_address:
        return

    # Always use mid-tier confirmations * 2 for restocking fee sweeps
    # (never trust petty-tier confirmations for fund movements)
    if payment.coin_type == "XMR":
        required_confirmations = 10 * 2  # XMR mid-tier * 2 = 20
    elif payment.coin_type == "DOGE":
        required_confirmations = 6 * 2  # DOGE mid-tier * 2 = 12
    else:
        required_confirmations = int(payment.confirmations_required) * 2  # Fallback

    current_confirmations = getattr(payment, "refund_confirmations", 0) or 0

    if current_confirmations < required_confirmations:
        log.payment_info(
            payment,
            f"Restocking fee sweep requires {required_confirmations} confirmations, refund has {current_confirmations} - waiting",
        )
        return

    coin_config = get_coin_config(payment.coin_type)
    atomic_units = coin_config["atomic_units"]
    fee_amount = int(refund_details["fee_amount"] * atomic_units)

    if fee_amount <= 0:
        return

    try:
        # Small delay to ensure refund tx is processed
        time.sleep(2)

        if payment.coin_type == "XMR":
            # Smart sweep: Use exact 9% amount with sweep_all fallback for safety
            client = get_crypto_client(settings, "XMR")

            # Get current balance in this specific subaddress
            balance_result = client._call(
                "get_balance",
                {
                    "account_index": payment.account_index,
                    "address_indices": [payment.subaddress_index],
                },
            )
            current_balance = balance_result.get("per_subaddress", [{}])[0].get(
                "balance", 0
            )

            # Simple logic: send min(balance, expected_fee)
            amount_to_send = min(current_balance, fee_amount)

            if amount_to_send > 0:
                transfer_result = client._call(
                    "transfer",
                    {
                        "destinations": [
                            {
                                "amount": amount_to_send,
                                "address": payment.shop_sweep_to_address,
                            }
                        ],
                        "account_index": payment.account_index,
                        "subaddr_indices": [payment.subaddress_index],
                        "priority": 1,
                        "get_tx_hex": True,
                        "do_not_relay": False,
                    },
                )
                fee_tx_hash = transfer_result.get("tx_hash")
                actual_swept = amount_to_send
                log.sweep_operation(
                    payment,
                    f"XMR restocking fee sent {amount_to_send} (balance: {current_balance}, expected: {fee_amount})",
                )
            else:
                fee_tx_hash = None
                actual_swept = 0
                log.payment_warning(payment, "XMR restocking fee: No balance available")

        elif payment.coin_type == "DOGE":
            # Smart sweep: Use exact 9% amount with balance check for safety
            client = get_crypto_client(settings, "DOGE")
            current_balance = client.getbalance()
            current_balance_atomic = int(current_balance * atomic_units)

            # Simple logic: send min(balance, expected_fee)
            amount_to_send_atomic = min(current_balance_atomic, fee_amount)

            if amount_to_send_atomic > 0:
                amount_to_send_crypto = float(
                    Decimal(amount_to_send_atomic) / atomic_units
                )
                fee_tx_hash = client._call(
                    "sendtoaddress",
                    [
                        payment.shop_sweep_to_address,
                        amount_to_send_crypto,
                        "",  # comment
                        "",  # comment_to
                        True,  # subtractfeefromamount
                    ],
                )
                actual_swept = amount_to_send_atomic
                log.sweep_operation(
                    payment,
                    f"DOGE restocking fee sent {amount_to_send_atomic} (balance: {current_balance_atomic}, expected: {fee_amount})",
                )
            else:
                fee_tx_hash = None
                actual_swept = 0
                log.payment_warning(
                    payment, "DOGE restocking fee: No balance available"
                )
        else:
            log.payment_warning(
                payment,
                f"Unsupported coin type for restocking fee sweep: {payment.coin_type}",
            )
            return

        if fee_tx_hash:
            log.sweep_operation(
                payment, f"{context} restocking fee swept", fee_tx_hash, actual_swept
            )

    except Exception as e:
        log.payment_error(
            payment, f"Failed to sweep {context.lower()} restocking fee", e
        )


def process_confirmed_payment(env_request, crypto_payment, client, payment_rescue=None):
    """
    Process a fully confirmed payment with proper order of operations:
    1. Finalize invoice first (always)
    2. Handle overpayment refunds (if applicable)
    3. Sweep restocking fees (if refund occurred)
    4. Auto-sweep remaining invoice amount to shop (last)

    Args:
        env_request: Environment request object
        crypto_payment: CryptoPayment object
        client: Crypto client
        payment_rescue: PaymentRescue instance (optional)

    Returns:
        dict with processing results
    """
    results = {
        "invoice_finalized": False,
        "overpayment_refund": None,
        "restocking_fee_swept": False,
        "auto_sweep": None,
        "final_status": None,
    }

    log.payment_info(
        crypto_payment, "Processing confirmed payment with proper order of operations"
    )

    try:
        # STEP 1: Always finalize invoice first (customer gets their product)
        # Check if invoice already finalized to make this idempotent
        if not crypto_payment.is_finalized():
            log.payment_info(crypto_payment, "Step 1: Finalizing invoice")
            finalize_invoice(env_request, crypto_payment, send_emails=True)
            results["invoice_finalized"] = True
        else:
            log.payment_info(
                crypto_payment, "Step 1: Invoice already finalized - skipping"
            )
            results["invoice_finalized"] = True  # Already done

        # STEP 2: Handle overpayment refunds (if applicable)
        if payment_rescue and crypto_payment.refund_address:
            coin_config = get_coin_config(crypto_payment.coin_type)
            atomic_units = coin_config["atomic_units"]
            received_crypto = Decimal(crypto_payment.received_amount) / atomic_units
            expected_crypto = Decimal(crypto_payment.expected_amount) / atomic_units

            # Check if this is an overpayment that exceeds threshold
            refund_details = payment_rescue.handle_overpayment(
                crypto_payment,
                expected_crypto,
                received_crypto,
                crypto_payment.invoice.user if crypto_payment.invoice else None,
            )

            if refund_details:
                log.refund_operation(crypto_payment, "processing overpayment")
                crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_OVERPAY
                crypto_payment.refund_reason = refund_details["reason"]

                # Check if refund already processed to make this idempotent
                if not crypto_payment.refund_tx_hash:
                    # Attempt overpayment refund
                    result = payment_rescue.execute_refund(
                        refund_details, crypto_payment
                    )
                    results["overpayment_refund"] = result
                else:
                    # Refund already processed successfully in previous attempt
                    log.refund_operation(
                        crypto_payment,
                        "already processed",
                        crypto_payment.refund_tx_hash,
                    )
                    result = {"success": True, "tx_hash": crypto_payment.refund_tx_hash}
                    results["overpayment_refund"] = result

                if result["success"]:
                    log.refund_operation(
                        crypto_payment, "successful", result["tx_hash"]
                    )
                    # Set refund details but keep in overpaid status for now
                    crypto_payment.refund_tx_hash = result["tx_hash"]
                    crypto_payment.refund_confirmations = 0

                    # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                    # The same transaction does both refund AND shop sweep, so record it as swept too
                    if not crypto_payment.swept_tx_hash:
                        # Calculate shop sweep amount: received - refund - fees
                        shop_sweep_amount = max(
                            0,
                            crypto_payment.received_amount
                            - crypto_payment.refund_amount,
                        )
                        # Note: Transaction fees are deducted automatically by the network

                        crypto_payment.swept_tx_hash = result["tx_hash"]
                        crypto_payment.swept_amount = shop_sweep_amount
                        crypto_payment.swept_timestamp = now_timestamp()
                        log.payment_info(
                            crypto_payment,
                            f"Multi-output transaction also sweeps {shop_sweep_amount} atomic units to shop - marked as swept with same TX hash",
                        )

                    # Note: Restocking fee will be swept after refund confirmation
                    results["restocking_fee_swept"] = (
                        False  # Will happen later when refund is confirmed
                    )
                    # Will set final status at end of function
                else:
                    log.payment_error(
                        crypto_payment,
                        "Overpayment refund failed - will retry",
                        result["error"],
                    )
                    # Don't proceed to auto-sweep if refund failed - keep in overpaid status for retry
                    results["final_status"] = CryptoPayment.STATUS_CONFIRMED_OVERPAY
                    return results
            else:
                # Check if there's actually an overpayment (not exact match)
                if received_crypto > expected_crypto:
                    # Overpayment within threshold - will confirm normally at end
                    log.payment_info(crypto_payment, "Overpayment within 5% threshold")
        else:
            # Normal payment - will confirm at end
            pass

        # STEP 4: Auto-sweep only the invoice amount (not entire wallet) - LAST
        if crypto_payment.shop_sweep_to_address:
            log.payment_info(crypto_payment, "Step 4: Auto-sweeping invoice amount")

            # Calculate exact amount to sweep (expected invoice amount only)
            sweep_success = auto_sweep_payment(
                client, crypto_payment, env_request.dbsession
            )
            results["auto_sweep"] = {"success": sweep_success}

            if sweep_success:
                log.payment_info(crypto_payment, "Auto-sweep successful")
            else:
                log.payment_error(crypto_payment, "Auto-sweep failed")
        else:
            log.payment_info(crypto_payment, "No shop sweep address configured")

        # STEP 5: Set terminal status ONLY at the very end when everything succeeded
        if results.get("overpayment_refund") and results["overpayment_refund"].get(
            "success"
        ):
            # Overpayment refund completed successfully
            crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED
            results["final_status"] = CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED
            log.payment_info(
                crypto_payment, "Fully processed - overpayment refunded and completed"
            )
        else:
            # Normal payment or overpayment within threshold
            crypto_payment.status = CryptoPayment.STATUS_CONFIRMED
            results["final_status"] = CryptoPayment.STATUS_CONFIRMED
            log.payment_info(crypto_payment, "Fully processed - confirmed")

        return results

    except Exception as e:
        log.payment_error(crypto_payment, "Error processing confirmed payment", e)
        results["error"] = str(e)
        return results


def auto_sweep_payment(client, crypto_payment: CryptoPayment, dbsession=None):
    """Auto-sweep funds from a confirmed payment to the shop's cold wallet."""
    log.payment_info(crypto_payment, "Starting auto-sweep check")

    # Dispatch to coin-specific sweep function
    if crypto_payment.coin_type == "XMR":
        return auto_sweep_payment_xmr(client, crypto_payment, dbsession)
    elif crypto_payment.coin_type == "DOGE":
        return auto_sweep_payment_doge(client, crypto_payment, dbsession)
    else:
        log.payment_error(
            crypto_payment,
            f"Unsupported coin type for sweep: {crypto_payment.coin_type}",
        )
        return False


def auto_sweep_payment_xmr(client, crypto_payment: CryptoPayment, dbsession=None):
    """Auto-sweep XMR funds from a confirmed payment to the shop's cold wallet."""
    log.payment_info(crypto_payment, "Starting XMR auto-sweep check")

    if not crypto_payment.shop_sweep_to_address:
        log.payment_info(crypto_payment, "No sweep address configured")
        return False

    if crypto_payment.is_swept:
        log.payment_info(crypto_payment, "Already swept")
        return True

    log.payment_info(
        crypto_payment, f"Needs sweep to {crypto_payment.shop_sweep_to_address}"
    )

    try:
        # Get balance for the account
        coin_config = get_coin_config("XMR")
        atomic_units = coin_config["atomic_units"]

        result = client._call(
            "get_balance", {"account_index": crypto_payment.account_index}
        )
        unlocked_balance = Decimal(result.get("unlocked_balance", 0)) / atomic_units

        log.payment_info(
            crypto_payment,
            f"Account {crypto_payment.account_index} unlocked balance: {unlocked_balance} XMR",
        )

        # Calculate sweep amount for THIS SPECIFIC payment only - use expected amount
        payment_amount_xmr = Decimal(crypto_payment.expected_amount) / atomic_units

        # If no unlocked balance, funds are still locked (10-block lock time)
        if unlocked_balance == 0:
            log.payment_info(
                crypto_payment,
                "No unlocked balance - funds still locked, will retry later",
            )
            # Don't mark as swept - funds are just locked!
            return False

        # Sweep funds from this specific subaddress only
        log.sweep_operation(
            crypto_payment,
            f"Sweeping funds from account {crypto_payment.account_index} subaddress {crypto_payment.subaddress_index} to {crypto_payment.shop_sweep_to_address}",
        )

        # Check for pending duplicate refunds that need this account's funds
        pending_refund_amount_xmr = Decimal("0")
        if dbsession:
            pending_duplicates = (
                dbsession.query(CryptoPayment)
                .filter(
                    CryptoPayment.coin_type == "XMR",
                    CryptoPayment.account_index == crypto_payment.account_index,
                    CryptoPayment.status == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                    CryptoPayment.refund_amount > 0,
                )
                .all()
            )

            for dup in pending_duplicates:
                dup_refund_xmr = Decimal(dup.refund_amount or 0) / atomic_units
                pending_refund_amount_xmr += dup_refund_xmr
                log.refund_operation(
                    dup, f"Reserving {dup_refund_xmr} XMR for pending duplicate refund"
                )

        # Check if account has enough unlocked balance for this payment and pending refunds
        payment_amount_piconero = crypto_payment.expected_amount
        payment_amount_xmr = Decimal(payment_amount_piconero) / atomic_units
        total_needed_xmr = payment_amount_xmr + pending_refund_amount_xmr

        if unlocked_balance < total_needed_xmr:
            log.payment_info(
                crypto_payment,
                f"Account unlocked balance ({unlocked_balance} XMR) is less than payment amount ({payment_amount_xmr} XMR) plus pending refunds ({pending_refund_amount_xmr} XMR) - insufficient funds or funds still locked",
            )
            return False

        log.payment_info(
            crypto_payment,
            f"Account has sufficient unlocked balance ({unlocked_balance} XMR) for payment amount ({payment_amount_xmr} XMR)",
        )

        # Verify this subaddress has the expected transfer
        try:
            transfers_result = client._call(
                "get_transfers",
                {
                    "in": True,
                    "out": False,
                    "pending": False,
                    "failed": False,
                    "pool": False,
                    "account_index": crypto_payment.account_index,
                    "subaddr_indices": [crypto_payment.subaddress_index],
                },
            )

            if "in" not in transfers_result or not transfers_result["in"]:
                log.payment_error(
                    crypto_payment,
                    f"No incoming transfers found for subaddress {crypto_payment.subaddress_index}",
                )
                return False

            log.payment_info(
                crypto_payment,
                f"Found {len(transfers_result['in'])} incoming transfers for subaddress {crypto_payment.subaddress_index}",
            )

        except Exception as e:
            log.error_with_context("Failed to verify subaddress transfers", e)
            return False

        # Use transfer but reduce amount to account for fees
        # Get dynamic fee estimate by doing a test transfer with do_not_relay=true
        try:
            # Estimate fee by doing a test transfer without broadcasting
            # Use 96% of amount to leave room for fee in the same subaddress
            test_amount_piconero = int(payment_amount_piconero * Decimal("0.96"))

            test_transfer_result = client._call(
                "transfer",
                {
                    "destinations": [
                        {
                            "address": crypto_payment.shop_sweep_to_address,
                            "amount": test_amount_piconero,
                        }
                    ],
                    "account_index": crypto_payment.account_index,
                    "subaddr_indices": [crypto_payment.subaddress_index],
                    "priority": 1,
                    "do_not_relay": True,  # Don't broadcast, just estimate
                    "get_tx_metadata": True,
                },
            )
            dynamic_fee_piconero = int(
                test_transfer_result.get("fee", 100000000000)
            )  # Fallback to ~0.0001 XMR
            # Add 10% margin to the dynamic fee estimate to ensure sweep always works
            estimated_fee_piconero = int(dynamic_fee_piconero * Decimal("1.1"))
            log.payment_info(
                crypto_payment,
                f"Dynamic fee estimate: {dynamic_fee_piconero / atomic_units} XMR, using {estimated_fee_piconero / atomic_units} XMR (with 10% margin)",
            )
        except Exception as e:
            # Fallback based on historical data: actual fees ~0.0000306 XMR
            # Use 3x multiplier for safety margin
            estimated_fee_piconero = int(
                Decimal("0.0000918") * atomic_units
            )  # ~91,800,000 piconero (3x typical fee)
            log.error_with_context(
                f"Failed to get dynamic fee estimate, using 3x typical fee as fallback: {e}",
                e,
            )

        # Calculate transfer amount: payment minus fee and reserve for pending refunds
        reserved_for_refunds_piconero = int(pending_refund_amount_xmr * atomic_units)
        available_for_sweep = (
            payment_amount_piconero
            - estimated_fee_piconero
            - reserved_for_refunds_piconero
        )
        transfer_amount_piconero = max(0, available_for_sweep)
        transfer_amount_xmr = Decimal(transfer_amount_piconero) / atomic_units

        log.sweep_operation(
            crypto_payment,
            f"transferring {transfer_amount_xmr} XMR",
            amount=transfer_amount_piconero,
        )

        result = client._call(
            "transfer",
            {
                "destinations": [
                    {
                        "address": crypto_payment.shop_sweep_to_address,
                        "amount": transfer_amount_piconero,
                    }
                ],
                "account_index": crypto_payment.account_index,
                "subaddr_indices": [crypto_payment.subaddress_index],
                "priority": 1,
                "get_tx_hex": False,
            },
        )

        # Monero transfer returns tx_hash directly, not in a list
        tx_hash = result.get("tx_hash")
        fee = result.get("fee", 0)

        if tx_hash:
            # Mark this payment as swept
            # Record the actual amount transferred (payment amount minus fee)
            total_swept = transfer_amount_piconero

            crypto_payment.swept_amount = int(total_swept)
            crypto_payment.swept_tx_hash = tx_hash
            crypto_payment.swept_timestamp = now_timestamp()
            crypto_payment.swept_network_fee = fee
            crypto_payment.swept_confirmations = 0  # Start tracking confirmations
            # Status stays as CONFIRMED until sweep is confirmed
            # crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_COMPLETE
            if dbsession:
                dbsession.add(crypto_payment)
            log.sweep_operation(
                crypto_payment, "auto-sweep successful", tx_hash, total_swept
            )
            return True
        else:
            log.payment_error(crypto_payment, "Sweep failed", result)
            return False

    except Exception as e:
        log.payment_error(crypto_payment, "Auto-sweep error", e)
        return False


def auto_sweep_payment_doge(client, crypto_payment: CryptoPayment, dbsession=None):
    """Auto-sweep DOGE funds from a confirmed payment to the shop's cold wallet."""
    log.payment_info(crypto_payment, "Starting DOGE auto-sweep check")

    if not crypto_payment.shop_sweep_to_address:
        log.payment_info(crypto_payment, "No sweep address configured")
        return False

    if crypto_payment.is_swept:
        log.payment_info(crypto_payment, "Already swept")
        return True

    log.payment_info(
        crypto_payment, f"Needs sweep to {crypto_payment.shop_sweep_to_address}"
    )

    try:
        coin_config = get_coin_config("DOGE")
        atomic_units = coin_config["atomic_units"]
        min_sweep_balance = coin_config["min_sweep_balance"]

        # Get wallet balance
        balance = Decimal(str(client.getbalance()))

        log.payment_info(crypto_payment, f"Wallet balance: {balance} DOGE")

        # Calculate payment amount in DOGE - use expected amount
        payment_amount_doge = Decimal(crypto_payment.expected_amount) / atomic_units

        # If balance is too low, return false to try again later
        if balance < min_sweep_balance:
            log.payment_info(
                crypto_payment, "Balance too low to sweep - insufficient funds"
            )
            return False

        # Get dynamic fee estimate for more accurate sweep amount
        try:
            # Use estimatesmartfee to get current network fee estimate
            # Use 6 block target (~1 hour) instead of 2 blocks for cheaper fees (matches quote logic)
            fee_estimate_result = client._call("estimatesmartfee", [6])
            if fee_estimate_result and "feerate" in fee_estimate_result:
                # feerate is in DOGE per KB, estimate transaction size as ~0.25KB (matches quote logic)
                network_feerate = float(fee_estimate_result["feerate"])

                # Cap fee rate at reasonable maximum (0.1 DOGE/KB = ~$0.025/KB) - matches quote logic
                max_reasonable_feerate = 0.1
                if network_feerate > max_reasonable_feerate:
                    log.payment_warning(
                        crypto_payment,
                        f"Network fee rate {network_feerate} DOGE/KB is excessive for sweep, capping at {max_reasonable_feerate} DOGE/KB",
                    )
                    network_feerate = max_reasonable_feerate

                estimated_fee_doge = network_feerate * 0.25
                log.sweep_operation(
                    crypto_payment,
                    f"Dynamic DOGE fee estimate: {network_feerate} DOGE/KB * 0.25KB = {estimated_fee_doge} DOGE",
                )
            else:
                # Fallback to reasonable fee if estimatesmartfee fails
                estimated_fee_doge = 0.002  # Matches quote fallback
                log.error_with_context(
                    "estimatesmartfee failed, using fallback fee", None
                )
        except Exception as e:
            # Fallback to reasonable fee if RPC call fails
            estimated_fee_doge = 0.002  # Matches quote fallback
            log.payment_warning(
                crypto_payment,
                f"Failed to get dynamic DOGE fee estimate, using fallback: {e}",
            )

        # Check for pending duplicate refunds that need this wallet's funds
        pending_refund_amount = Decimal("0")
        if dbsession:
            pending_duplicates = (
                dbsession.query(CryptoPayment)
                .filter(
                    CryptoPayment.coin_type == "DOGE",
                    CryptoPayment.address == crypto_payment.address,
                    CryptoPayment.status == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                    CryptoPayment.refund_amount > 0,
                )
                .all()
            )

            for dup in pending_duplicates:
                dup_refund_doge = Decimal(dup.refund_amount or 0) / atomic_units
                pending_refund_amount += dup_refund_doge
                log.refund_operation(
                    dup,
                    f"Reserving {dup_refund_doge} DOGE for pending duplicate refund",
                )

        # Only sweep the expected payment amount, not the entire balance
        # This leaves any duplicate payments or overpayments in the wallet for refunding
        if balance < payment_amount_doge:
            log.payment_info(
                crypto_payment,
                f"Insufficient balance: have {balance} DOGE but need {payment_amount_doge} DOGE",
            )
            return False

        # Check if we have enough after accounting for pending refunds
        total_needed = payment_amount_doge + pending_refund_amount
        if balance < total_needed:
            log.payment_info(
                crypto_payment,
                f"Insufficient balance for sweep and pending refunds: have {balance} DOGE but need {total_needed} DOGE",
            )
            return False

        sweep_amount = payment_amount_doge

        log.sweep_operation(
            crypto_payment,
            f"Sweeping {sweep_amount} DOGE to {crypto_payment.shop_sweep_to_address}",
        )

        # Send the sweep transaction
        # Use subtractfeefromamount=True so network fee is deducted from the sweep amount
        tx_hash = client._call(
            "sendtoaddress",
            [
                crypto_payment.shop_sweep_to_address,
                float(sweep_amount),
                f"Sweep for invoice {crypto_payment.invoice.id}",
                "",  # comment_to
                True,  # subtractfeefromamount
            ],
        )

        if tx_hash:
            # Mark this payment as swept
            swept_amount_koinu = int(sweep_amount * atomic_units)

            crypto_payment.swept_amount = swept_amount_koinu
            crypto_payment.swept_tx_hash = tx_hash
            crypto_payment.swept_timestamp = now_timestamp()
            # Note: DOGE RPC doesn't return fee info easily, so we leave it None
            crypto_payment.swept_network_fee = None
            crypto_payment.swept_confirmations = 0  # Start tracking confirmations
            # Status stays as CONFIRMED until sweep is confirmed
            # crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_COMPLETE
            if dbsession:
                dbsession.add(crypto_payment)

            log.sweep_operation(
                crypto_payment,
                f"DOGE auto-sweep successful! TX: {tx_hash}, Swept: {sweep_amount} DOGE",
            )
            return True
        else:
            log.payment_error(crypto_payment, "DOGE sweep failed")
            return False

    except Exception as e:
        log.payment_error(crypto_payment, "DOGE auto-sweep error", e)
        return False


def get_dogecoin_incoming_transfers(client, crypto_payment: CryptoPayment):
    """Get incoming transfers for a Dogecoin payment address."""
    try:
        address = crypto_payment.address

        # Get received amount by address (with minimum 0 confirmations for mempool detection)
        received_amount = client.getreceivedbyaddress(address, 0)

        # Get recent transactions for this address
        transactions = client.listtransactions(
            "*", 100, 0
        )  # Get recent 100 transactions

        # Filter for transactions to our address
        incoming_txs = []
        for tx in transactions:
            if (
                tx.get("address") == address
                and tx.get("category") == "receive"
                and tx.get("amount", 0) > 0
            ):

                # Convert to format similar to Monero transfers
                incoming_txs.append(
                    {
                        "txid": tx.get("txid", ""),
                        "amount": int(
                            float(tx.get("amount", 0)) * 100_000_000
                        ),  # Convert to koinu
                        "confirmations": tx.get("confirmations", 0),
                        "address": address,
                    }
                )

        log.payment_info(
            crypto_payment,
            f"Found {len(incoming_txs)} incoming DOGE transfers for address {address}",
        )
        return incoming_txs

    except Exception as e:
        log.payment_error(crypto_payment, "Error getting DOGE transfers", e)
        return []


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Crypto watcher: confirm payments and finalize invoices"
    )
    p.add_argument("config_uri", help="Pyramid config file, e.g. development.ini")
    p.add_argument(
        "--interval", type=int, default=20, help="Polling interval seconds (default 20)"
    )
    p.add_argument("--once", action="store_true", help="Run a single pass then exit")
    return p.parse_args(argv[1:])


def summarize_txs(transfers: List[dict]):
    total = 0
    txids = []
    confs = []
    for t in transfers:
        # monero-wallet-rpc returns atomic units in `amount` and integer `confirmations`
        amt = int(t.get("amount", 0) or 0)
        total += amt
        txid = t.get("txid") or t.get("transaction_id")
        if txid:
            txids.append(txid)
        c = t.get("confirmations")
        if isinstance(c, int):
            confs.append(c)
    min_conf = min(confs) if confs else 0
    return total, list(dict.fromkeys(txids)), min_conf


# Removed mark_payment_voided - no longer needed without Payment model


class ShopContextRequestWrapper:
    """Wrapper to provide shop domain context for email generation in crypto watcher."""

    def __init__(self, original_request, shop):
        self._original_request = original_request
        self._shop = shop

        # Use shop's domain_name if available, otherwise fallback to original request
        if shop and shop.domain_name:
            self._domain = shop.domain_name
            # Construct full URL for the shop's domain
            self._host_url = f"https://{shop.domain_name}"
        else:
            # Fallback to original request values
            self._domain = getattr(original_request, "domain", "localhost")
            self._host_url = getattr(original_request, "host_url", "http://localhost")

    def __getattr__(self, name):
        # Proxy all other attributes to the original request
        # Handle missing attributes gracefully for test environments
        return getattr(self._original_request, name, None)

    @property
    def domain(self):
        return self._domain

    @property
    def host_url(self):
        return self._host_url

    @property
    def app(self):
        """Proxy app attribute from original request."""
        return getattr(self._original_request, "app", {})


def create_shop_context_request(env_request, crypto_payment: CryptoPayment):
    """Create a request wrapper with shop domain context for email generation."""
    # Get shop through the relationship: crypto_payment -> invoice -> shop
    shop = crypto_payment.invoice.shop if crypto_payment.invoice else None
    return ShopContextRequestWrapper(env_request, shop)


def check_inventory_availability(env_request, crypto_payment: CryptoPayment):
    """Check if all physical products in the invoice have sufficient inventory.

    Returns:
        tuple: (is_available: bool, out_of_stock_items: list)
    """
    invoice = crypto_payment.invoice
    out_of_stock_items = []

    if crypto_payment.shop_location:
        for item in invoice.line_items:
            product = item.product
            if getattr(product, "is_physical", False):
                inv = get_inventory_by_product_and_shop_location(
                    env_request.dbsession, product.id, crypto_payment.shop_location.id
                )
                available_qty = inv.quantity if inv else 0
                if available_qty < item.quantity:
                    out_of_stock_items.append(
                        {
                            "product": product,
                            "requested": item.quantity,
                            "available": available_qty,
                        }
                    )

    return len(out_of_stock_items) == 0, out_of_stock_items


def finalize_invoice(env_request, crypto_payment: CryptoPayment, send_emails=True):
    invoice: Invoice = crypto_payment.invoice

    # Check inventory availability for physical goods BEFORE finalizing
    is_available, out_of_stock = check_inventory_availability(
        env_request, crypto_payment
    )

    if not is_available:
        # Inventory not available - need to refund WITHOUT restocking fee
        log.payment_warning(
            crypto_payment,
            f"Cannot be fulfilled - out of stock items: "
            f"{[item['product'].name for item in out_of_stock]}",
        )

        # Set refund reason for out of stock
        crypto_payment.refund_reason = f"Out of stock: {', '.join([item['product'].name for item in out_of_stock])}"
        env_request.dbsession.add(crypto_payment)

        # Handle out of stock situation
        if crypto_payment.refund_address:
            # Customer provided refund address - do full refund
            client = get_crypto_client(
                env_request.registry.settings, crypto_payment.coin_type
            )
            coin_config = get_coin_config(crypto_payment.coin_type)

            # Calculate full refund amount
            refund_amount_crypto = (
                Decimal(crypto_payment.received_amount) / coin_config["atomic_units"]
            )

            try:
                # Process the refund sweep - use sweep_all to get ALL funds from this subaddress
                if crypto_payment.coin_type == "XMR":
                    sweep_result = client._call(
                        "sweep_all",
                        {
                            "account_index": crypto_payment.account_index,
                            "address": crypto_payment.refund_address,
                            "subaddr_indices": [
                                crypto_payment.subaddress_index
                            ],  # Only this payment's subaddress
                            "priority": 1,  # Normal priority
                            "get_tx_hex": True,
                            "do_not_relay": False,
                        },
                    )
                    tx_hash = sweep_result.get("tx_hash_list", [None])[0]
                elif crypto_payment.coin_type == "DOGE":
                    # For Dogecoin, use sendtoaddress with fee subtraction for full refund
                    tx_hash = client._call(
                        "sendtoaddress",
                        [
                            crypto_payment.refund_address,
                            float(refund_amount_crypto),
                            "Out of stock refund",  # comment
                            "",  # comment_to
                            True,  # subtractfeefromamount - ensures ALL funds are sent
                        ],
                    )
                else:
                    tx_hash = None

                if tx_hash:
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "OUT_OF_STOCK_REFUNDED",
                        f"TX: {tx_hash}",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED
                    crypto_payment.refund_tx_hash = tx_hash
                    crypto_payment.refund_amount = crypto_payment.received_amount
                    log.refund_operation(
                        crypto_payment,
                        f"Full refund processed for out of stock. "
                        f"Amount: {refund_amount_crypto} {crypto_payment.coin_type}",
                        tx_hash=tx_hash,
                    )
                else:
                    log.payment_error(
                        crypto_payment, "Failed to process full refund - no tx hash"
                    )

            except Exception as e:
                log.payment_error(crypto_payment, "Failed to process full refund", e)
        else:
            # No refund address - sweep all funds to shop's cold storage
            if crypto_payment.shop_sweep_to_address:
                client = get_crypto_client(
                    env_request.registry.settings, crypto_payment.coin_type
                )
                coin_config = get_coin_config(crypto_payment.coin_type)

                try:
                    # Sweep all funds from this subaddress to shop's cold storage
                    if crypto_payment.coin_type == "XMR":
                        sweep_result = client._call(
                            "sweep_all",
                            {
                                "account_index": crypto_payment.account_index,
                                "address": crypto_payment.shop_sweep_to_address,
                                "subaddr_indices": [
                                    crypto_payment.subaddress_index
                                ],  # Only this payment's subaddress
                                "priority": 1,  # Normal priority
                                "get_tx_hex": True,
                                "do_not_relay": False,
                            },
                        )
                        tx_hash = sweep_result.get("tx_hash_list", [None])[0]
                        swept_amount = sweep_result.get("amount_list", [0])[0]
                    elif crypto_payment.coin_type == "DOGE":
                        # For Dogecoin, sweep ALL funds to shop's address
                        refund_amount_crypto = (
                            Decimal(crypto_payment.received_amount)
                            / coin_config["atomic_units"]
                        )
                        tx_hash = client._call(
                            "sendtoaddress",
                            [
                                crypto_payment.shop_sweep_to_address,
                                float(refund_amount_crypto),
                                "Out of stock - no refund address",  # comment
                                "",  # comment_to
                                True,  # subtractfeefromamount - ensures ALL funds are sent
                            ],
                        )
                        swept_amount = crypto_payment.received_amount
                    else:
                        tx_hash = None
                        swept_amount = 0

                    if tx_hash:
                        crypto_payment.status = (
                            CryptoPayment.STATUS_OUT_OF_STOCK_NOT_REFUNDED
                        )
                        crypto_payment.swept_tx_hash = tx_hash
                        crypto_payment.swept_amount = swept_amount
                        crypto_payment.swept_timestamp = now_timestamp()
                        # Delete invoice for terminal state
                        delete_invoice_for_terminal_state(
                            env_request.dbsession, crypto_payment
                        )
                        log.sweep_operation(
                            crypto_payment,
                            f"Out of stock payment swept to shop cold storage. "
                            f"Amount: {swept_amount} atomic units",
                            tx_hash=tx_hash,
                        )
                    else:
                        log.payment_error(
                            crypto_payment,
                            "Failed to sweep out of stock payment to shop storage",
                        )

                except Exception as e:
                    log.payment_error(
                        crypto_payment,
                        "Failed to sweep out of stock payment to shop",
                        e,
                    )
            else:
                log.payment_error(
                    crypto_payment,
                    "CONFIGURATION ERROR: Out of stock payment has no refund address and no shop sweep address",
                )
                log.state_transition(
                    crypto_payment,
                    crypto_payment.status,
                    "OUT_OF_STOCK_NOT_REFUNDED",
                    "no refund or sweep address",
                )
                crypto_payment.status = CryptoPayment.STATUS_OUT_OF_STOCK_NOT_REFUNDED
                # Delete invoice for terminal state
                delete_invoice_for_terminal_state(env_request.dbsession, crypto_payment)

        # Send notification email about the refund
        if invoice.user.email and not crypto_payment.refund_email_sent:
            # TODO: Send out of stock refund notification email
            # When implemented, set: crypto_payment.refund_email_sent = True
            pass

        return False  # Invoice not finalized

    # Unlock products for the purchasing user and notify via email (mirrors Stripe flow)
    for line_item in invoice.line_items:
        line_item.product.unlock_for_user(invoice.user)
        env_request.dbsession.add(line_item.product)

    # Deactivate the user's current cart and create a new empty one
    # This mirrors the behavior in save_cart() for Stripe payments
    if invoice.user and invoice.shop:
        # Ensure objects are attached to the session
        env_request.dbsession.add(invoice.shop)
        env_request.dbsession.add(invoice.user)

        # Get the user's current active cart for this shop
        current_active_cart = invoice.shop.get_active_cart_for_user(invoice.user)
        log.payment_info(
            crypto_payment,
            f"Current active cart for user {invoice.user.id}: {current_active_cart.id if current_active_cart else 'None'}, "
            f"empty: {current_active_cart.is_empty if current_active_cart else 'N/A'}",
        )

        if current_active_cart and not current_active_cart.is_empty:
            # Create a new empty cart and make it active
            new_cart = invoice.shop.create_new_cart_for_user(invoice.user)
            log.payment_info(
                crypto_payment,
                f"Created new empty cart {new_cart.id} for user {invoice.user.id} after crypto payment confirmation",
            )
        else:
            log.payment_info(
                crypto_payment,
                f"Skipping cart deactivation for user {invoice.user.id} - cart is empty or doesn't exist",
            )

    # Emails (configurable)
    email_enabled = True
    try:
        settings = getattr(getattr(env_request, "registry", None), "settings", {}) or {}
        val = settings.get("app.email.enabled")
        if isinstance(val, str):
            email_enabled = val.strip().lower() in ("1", "true", "yes", "on")
        elif isinstance(val, bool):
            email_enabled = val
    except Exception:
        # Leave default True if anything goes wrong
        pass

    if email_enabled and send_emails:
        # Create a request wrapper with shop's domain context for emails
        email_request = create_shop_context_request(env_request, crypto_payment)

        # Check if purchase email has already been sent
        if not crypto_payment.purchase_email_sent:
            send_purchase_email(
                email_request,
                invoice.user.email,
                [item.product for item in invoice.line_items],
                invoice.total,
            )
            crypto_payment.purchase_email_sent = True

        # Check if sales email has already been sent
        if not crypto_payment.sales_email_sent:
            send_sale_email(
                email_request,
                invoice.shop,
                [item.product for item in invoice.line_items],
                invoice.total,
            )
            crypto_payment.sales_email_sent = True

    # Deduct inventory for physical products if a shop location is known
    if crypto_payment.shop_location:
        for item in invoice.line_items:
            product = item.product
            if getattr(product, "is_physical", False):
                inv = get_inventory_by_product_and_shop_location(
                    env_request.dbsession, product.id, crypto_payment.shop_location.id
                )
                if inv:
                    inv.quantity = max(0, int(inv.quantity) - int(item.quantity))
                    env_request.dbsession.add(inv)


def process_payment(
    env_request,
    crypto_payment: CryptoPayment,
    incoming_transfers: List[dict],
    client=None,
):
    """Process a single CryptoPayment given already-fetched incoming transfers.

    Mirrors the status and finalization logic for easier unit testing.
    """
    import json

    log.payment_info(
        crypto_payment,
        f"[DEBUG] Entering process_payment - status: {crypto_payment.status}, has_invoice: {crypto_payment.invoice is not None}, incoming_transfers: {len(incoming_transfers)}",
    )

    now_ms = int(time.time() * 1000)

    # Initialize payment rescue with correct client for this coin type
    try:
        coin_client = get_crypto_client(
            env_request.registry.settings, crypto_payment.coin_type
        )
        payment_rescue = PaymentRescue(env_request.dbsession, coin_client)
    except (ValueError, Exception):
        payment_rescue = None

    # Handle duplicate payment refunds (special case - always refund with 9% fee)
    #
    # This processes payments created by _create_duplicate_payment() for transactions
    # sent to already-paid quotes. Each duplicate payment:
    # 1. Uses stored received_amount (not incoming_transfers which may be stale)
    # 2. Calculates refund with 9% restocking fee
    # 3. Transitions to doublepay-refund-complete when successful
    # 4. Supports multiple duplicates (triple-pay, etc.) independently
    if crypto_payment.status == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED:
        # Check for refund address - use payment's or lookup saved address
        refund_address = crypto_payment.refund_address
        if not refund_address and crypto_payment.user_id:
            refund_address = _get_user_refund_address(
                env_request.dbsession, crypto_payment.user_id, crypto_payment.coin_type
            )
            if refund_address:
                # Update payment with the saved refund address
                crypto_payment.refund_address = refund_address
                env_request.dbsession.add(crypto_payment)
                log.payment_info(
                    crypto_payment,
                    f"Updated duplicate payment with saved refund address: {refund_address[:16]}...",
                )

        log.payment_info(
            crypto_payment,
            f"DOUBLEPAY_REFUND processing: "
            f"refund_address={refund_address[:16] if refund_address else 'None'}..., "
            f"incoming_transfers={len(incoming_transfers) if incoming_transfers else 0}, "
            f"payment_rescue={'available' if payment_rescue else 'None'}, "
            f"client={'available' if client else 'None'}",
        )

        # For duplicate payments, we need to look up the specific transaction since
        # incoming_transfers only contains current scanning window
        if crypto_payment.tx_hashes and payment_rescue and refund_address:
            try:
                stored_txids = json.loads(crypto_payment.tx_hashes or "[]")
                if stored_txids and client:
                    # Query the specific transaction by ID
                    if crypto_payment.coin_type == "XMR":
                        # For XMR, get ALL transfers and find our specific transaction
                        # Use get_transfers without height filtering to get historical data
                        res = (
                            client._call(
                                "get_transfers",
                                {
                                    "in": True,
                                    "out": False,
                                    "pending": True,
                                    "failed": False,
                                    "pool": True,
                                    "filter_by_height": False,  # Get ALL transfers
                                    "subaddr_indices": [
                                        crypto_payment.subaddress_index
                                    ],
                                    "account_index": crypto_payment.account_index,
                                },
                            )
                            or {}
                        )
                        all_incoming = res.get("in", []) or []
                        # Find our specific transaction
                        duplicate_transfers = [
                            tx for tx in all_incoming if tx.get("txid") in stored_txids
                        ]
                        incoming_transfers = duplicate_transfers
                        log.payment_info(
                            crypto_payment,
                            f"Found {len(duplicate_transfers)} duplicate transactions "
                            f"from stored txids: {stored_txids}",
                        )

                        # Update confirmation count for this specific duplicate payment transaction
                        if duplicate_transfers:
                            # Get confirmation count from the specific transaction
                            min_confirmations = min(
                                tx.get("confirmations", 0) for tx in duplicate_transfers
                            )
                            old_confirmations = crypto_payment.current_confirmations
                            crypto_payment.current_confirmations = min_confirmations
                            log.confirmation_update(
                                crypto_payment, old_confirmations, min_confirmations
                            )
                    else:
                        # For other coins, query by transaction ID directly
                        duplicate_transfers = []
                        for txid in stored_txids:
                            try:
                                tx_detail = client.gettransaction(txid)
                                if tx_detail:
                                    duplicate_transfers.append(tx_detail)
                            except Exception as e:
                                log.payment_warning(
                                    crypto_payment,
                                    f"Could not fetch transaction {txid}: {e}",
                                )
                        incoming_transfers = duplicate_transfers

                        # Update confirmation count for this specific duplicate payment transaction
                        if duplicate_transfers:
                            # Get confirmation count from the specific transaction
                            min_confirmations = min(
                                tx.get("confirmations", 0) for tx in duplicate_transfers
                            )
                            old_confirmations = crypto_payment.current_confirmations
                            crypto_payment.current_confirmations = min_confirmations
                            log.confirmation_update(
                                crypto_payment, old_confirmations, min_confirmations
                            )
            except (json.JSONDecodeError, TypeError) as e:
                log.payment_warning(crypto_payment, f"Invalid tx_hashes JSON: {e}")
                incoming_transfers = []

        # For duplicate payments, use the stored received_amount since incoming_transfers
        # might not contain the historical transaction data
        if payment_rescue and refund_address and crypto_payment.received_amount > 0:
            coin_config = get_coin_config(crypto_payment.coin_type)
            received_crypto = (
                Decimal(crypto_payment.received_amount) / coin_config["atomic_units"]
            )

            # For duplicate payments, we should have the user and invoice directly available
            # since they were copied from the original payment when created
            if crypto_payment.invoice and crypto_payment.invoice.user:
                user = crypto_payment.invoice.user
                refund_details = payment_rescue.handle_expired_payment(
                    crypto_payment, received_crypto, user
                )

                if refund_details:
                    # Update refund reason to be more specific
                    refund_details["reason"] = (
                        f"Duplicate payment: received {received_crypto} {crypto_payment.coin_type} to already-paid quote"
                    )

                    # Check if refund is economically viable
                    if not refund_details.get("economically_viable", True):
                        # Refund is not economically viable - transition to not-refunded state
                        log.payment_info(
                            crypto_payment,
                            f"Duplicate payment refund not economically viable: {refund_details['refund_amount']} {crypto_payment.coin_type} below threshold",
                        )
                        log.state_transition(
                            crypto_payment,
                            crypto_payment.status,
                            "DOUBLEPAY_NOT_REFUNDED",
                            "economically unviable refund",
                        )
                        crypto_payment.status = (
                            CryptoPayment.STATUS_DOUBLEPAY_NOT_REFUNDED
                        )
                        crypto_payment.refund_reason = f"Duplicate payment - refund economically unviable ({refund_details['refund_amount']} {crypto_payment.coin_type})"
                        # Store the unviable refund amount for record keeping
                        crypto_payment.refund_amount = int(
                            refund_details["refund_amount"]
                            * coin_config["atomic_units"]
                        )

                        # Send refund email notification
                        if crypto_payment.invoice and crypto_payment.invoice.user:
                            try:
                                # Create shop context request
                                email_request = create_shop_context_request(
                                    env_request, crypto_payment
                                )
                                send_refund_email(
                                    email_request,
                                    crypto_payment.invoice.user.email,
                                    crypto_payment,
                                    refund_details,
                                )
                                log.payment_info(
                                    crypto_payment,
                                    "Sent refund email for economically unviable duplicate payment",
                                )
                            except Exception as e:
                                log.payment_error(
                                    crypto_payment,
                                    f"Failed to send refund email for economically unviable duplicate payment: {e}",
                                )

                        env_request.dbsession.add(crypto_payment)
                        env_request.dbsession.flush()
                        return  # Exit early - no refund to process

                    log.refund_operation(
                        crypto_payment,
                        f"Duplicate payment eligible for refund: {refund_details}",
                    )

                    result = payment_rescue.execute_refund(
                        refund_details, crypto_payment
                    )
                    if result["success"]:
                        log.refund_operation(
                            crypto_payment,
                            "Refund executed for duplicate payment",
                            tx_hash=result["tx_hash"],
                        )
                        # Track the refund details
                        crypto_payment.refund_amount = int(
                            refund_details["refund_amount"]
                            * coin_config["atomic_units"]
                        )
                        crypto_payment.refund_tx_hash = result["tx_hash"]
                        crypto_payment.refund_reason = refund_details["reason"]

                        # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                        if not crypto_payment.swept_tx_hash:
                            # Calculate shop sweep amount: received - refund - fees
                            shop_sweep_amount = max(
                                0,
                                crypto_payment.received_amount
                                - crypto_payment.refund_amount,
                            )

                            crypto_payment.swept_tx_hash = result["tx_hash"]
                            crypto_payment.swept_amount = shop_sweep_amount
                            crypto_payment.swept_timestamp = now_timestamp()

                        # Transition to refund monitoring status
                        crypto_payment.status = (
                            CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE
                        )
                        env_request.dbsession.add(crypto_payment)
                        # CRITICAL: Flush immediately to prevent double-refund bug
                        env_request.dbsession.flush()
                        log.state_transition(
                            crypto_payment,
                            CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                            CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
                            "refund executed successfully",
                        )

                        # Send refund email notification if not already sent
                        if not crypto_payment.refund_email_sent:
                            try:
                                # Create shop context request using the duplicate payment (now has invoice)
                                email_request = create_shop_context_request(
                                    env_request, crypto_payment
                                )
                                send_refund_email(
                                    email_request,
                                    user.email,
                                    crypto_payment,
                                    refund_details,
                                )
                                crypto_payment.refund_email_sent = True
                                env_request.dbsession.add(crypto_payment)
                                log.payment_info(
                                    crypto_payment,
                                    "Sent refund email for duplicate payment",
                                )
                            except Exception as e:
                                # Log error but don't let email failure break duplicate payment processing
                                log.payment_error(
                                    crypto_payment,
                                    "Failed to send refund email for duplicate payment",
                                    e,
                                )
                                # Continue processing - email failure shouldn't prevent refund completion
                    else:
                        log.payment_error(
                            crypto_payment,
                            f"Refund failed for duplicate payment: {result['error']}",
                        )
                        # For failed refunds due to insufficient funds, keep trying but log the failure
                        # Status remains STATUS_DOUBLEPAY_REFUNDED for retry, but we could implement backoff logic here
                        log.payment_info(
                            crypto_payment,
                            "Duplicate payment refund failed - will retry on next cycle",
                        )
            else:
                log.payment_error(
                    crypto_payment,
                    "DATA ERROR: Duplicate payment has no invoice or user - this should not happen",
                )
                log.state_transition(
                    crypto_payment,
                    crypto_payment.status,
                    "DOUBLEPAY_NOT_REFUNDED",
                    "no invoice or user",
                )
                crypto_payment.status = CryptoPayment.STATUS_DOUBLEPAY_NOT_REFUNDED
                crypto_payment.refund_reason = (
                    "Duplicate payment - no invoice or user information available"
                )
        return  # Early return - duplicate payments don't need further processing

    # Handle expiry - early detection for refund scenario
    if crypto_payment.is_expired:
        crypto_payment.updated_timestamp = now_ms

        # Check if we received funds after expiry and can refund
        if (
            incoming_transfers
            and crypto_payment.invoice
            and crypto_payment.invoice.user
        ):
            total_recv, _, _ = summarize_txs(incoming_transfers)
            if total_recv > 0:
                # EARLY DETECTION: Mark for refund immediately (even in mempool)
                log.payment_info(
                    crypto_payment,
                    f"EARLY DETECTION - Late payment to expired quote: "
                    f"received {total_recv} atomic units - determining refund scenario",
                )

                # Check if refund address exists to determine final status immediately
                if crypto_payment.refund_address:
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "LATEPAY_REFUNDED",
                        "marked for refund",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_LATEPAY_REFUNDED
                else:
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "LATEPAY_NOT_REFUNDED",
                        "no refund address",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_LATEPAY_NOT_REFUNDED
                    crypto_payment.refund_reason = (
                        "Late payment - no refund address configured"
                    )
                    # Delete invoice for terminal state
                    delete_invoice_for_terminal_state(
                        env_request.dbsession, crypto_payment
                    )
                    log.payment_info(
                        crypto_payment,
                        "Expired payment marked as no-refund (no refund address)",
                    )
        else:
            # No funds received - just mark as expired
            log.state_transition(
                crypto_payment, crypto_payment.status, "EXPIRED", "no funds received"
            )
            crypto_payment.status = CryptoPayment.STATUS_EXPIRED

        env_request.dbsession.add(crypto_payment)

        # Execute refund logic if we have enough confirmations
        if (
            incoming_transfers
            and crypto_payment.invoice
            and crypto_payment.invoice.user
            and crypto_payment.status == CryptoPayment.STATUS_LATEPAY_REFUNDED
        ):
            total_recv, _, early_min_confs = summarize_txs(incoming_transfers)
            if (
                early_min_confs >= int(crypto_payment.confirmations_required)
                and total_recv > 0
            ):
                # Check if items are out of stock - if so, do FULL refund
                is_available, out_of_stock = check_inventory_availability(
                    env_request, crypto_payment
                )

                if not is_available:
                    # Out of stock - handle based on whether refund address exists
                    crypto_payment.refund_reason = f"Expired + Out of stock: {', '.join([item['product'].name for item in out_of_stock])}"

                    coin_config = get_coin_config(crypto_payment.coin_type)
                    refund_amount_crypto = (
                        Decimal(total_recv) / coin_config["atomic_units"]
                    )

                    if crypto_payment.refund_address:
                        # Customer provided refund address - do full refund
                        try:
                            if crypto_payment.coin_type == "XMR":
                                # Use sweep_all to get ALL funds from this subaddress
                                sweep_result = client._call(
                                    "sweep_all",
                                    {
                                        "account_index": crypto_payment.account_index,
                                        "address": crypto_payment.refund_address,
                                        "subaddr_indices": [
                                            crypto_payment.subaddress_index
                                        ],  # Only this payment's subaddress
                                        "priority": 1,
                                        "get_tx_hex": True,
                                        "do_not_relay": False,
                                    },
                                )
                                tx_hash = sweep_result.get("tx_hash_list", [None])[0]
                            elif crypto_payment.coin_type == "DOGE":
                                # Use subtractfeefromamount for full refund
                                tx_hash = client._call(
                                    "sendtoaddress",
                                    [
                                        crypto_payment.refund_address,
                                        float(refund_amount_crypto),
                                        "Out of stock refund",  # comment
                                        "",  # comment_to
                                        True,  # subtractfeefromamount
                                    ],
                                )
                            else:
                                tx_hash = None

                            if tx_hash:
                                crypto_payment.status = (
                                    CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED
                                )
                                crypto_payment.refund_tx_hash = tx_hash
                                crypto_payment.refund_amount = total_recv
                                log.refund_operation(
                                    crypto_payment,
                                    f"Full refund for expired+out of stock payment. "
                                    f"Amount: {refund_amount_crypto} {crypto_payment.coin_type}",
                                    tx_hash=tx_hash,
                                )
                        except Exception as e:
                            log.payment_error(
                                crypto_payment,
                                "Failed to process full refund for expired payment",
                                e,
                            )
                    else:
                        # No refund address - sweep to shop's cold storage
                        if crypto_payment.shop_sweep_to_address:
                            try:
                                if crypto_payment.coin_type == "XMR":
                                    sweep_result = client._call(
                                        "sweep_all",
                                        {
                                            "account_index": crypto_payment.account_index,
                                            "address": crypto_payment.shop_sweep_to_address,
                                            "subaddr_indices": [
                                                crypto_payment.subaddress_index
                                            ],  # Only this payment's subaddress
                                            "priority": 1,
                                            "get_tx_hex": True,
                                            "do_not_relay": False,
                                        },
                                    )
                                    tx_hash = sweep_result.get("tx_hash_list", [None])[
                                        0
                                    ]
                                    swept_amount = sweep_result.get("amount_list", [0])[
                                        0
                                    ]
                                elif crypto_payment.coin_type == "DOGE":
                                    # Sweep ALL funds to shop with fee subtraction
                                    tx_hash = client._call(
                                        "sendtoaddress",
                                        [
                                            crypto_payment.shop_sweep_to_address,
                                            float(refund_amount_crypto),
                                            "Out of stock - no refund address",  # comment
                                            "",  # comment_to
                                            True,  # subtractfeefromamount
                                        ],
                                    )
                                    swept_amount = total_recv
                                else:
                                    tx_hash = None
                                    swept_amount = 0

                                if tx_hash:
                                    crypto_payment.status = (
                                        CryptoPayment.STATUS_OUT_OF_STOCK_NOT_REFUNDED
                                    )
                                    crypto_payment.swept_tx_hash = tx_hash
                                    crypto_payment.swept_amount = swept_amount
                                    crypto_payment.swept_timestamp = now_timestamp()
                                    # Delete invoice for terminal state
                                    delete_invoice_for_terminal_state(
                                        env_request.dbsession, crypto_payment
                                    )
                                    log.sweep_operation(
                                        crypto_payment,
                                        f"Expired+out of stock payment swept to shop cold storage. "
                                        f"Amount: {swept_amount} atomic units",
                                        tx_hash=tx_hash,
                                    )
                            except Exception as e:
                                log.payment_error(
                                    crypto_payment,
                                    "Failed to sweep expired+out of stock payment",
                                    e,
                                )
                        else:
                            log.payment_error(
                                crypto_payment,
                                "CONFIGURATION ERROR: Expired+out of stock payment has no refund or sweep address",
                            )
                            crypto_payment.status = (
                                CryptoPayment.STATUS_OUT_OF_STOCK_NOT_REFUNDED
                            )
                            # Delete invoice for terminal state
                            delete_invoice_for_terminal_state(
                                env_request.dbsession, crypto_payment
                            )

                elif payment_rescue and crypto_payment.refund_address:
                    # Not out of stock - do normal expired refund with restocking fee
                    coin_config = get_coin_config(crypto_payment.coin_type)
                    received_crypto = Decimal(total_recv) / coin_config["atomic_units"]
                    refund_details = payment_rescue.handle_expired_payment(
                        crypto_payment, received_crypto, crypto_payment.invoice.user
                    )
                    if refund_details:
                        # Check if refund is economically viable
                        if not refund_details.get("economically_viable", True):
                            # Refund is not economically viable - transition to not-refunded state
                            log.payment_info(
                                crypto_payment,
                                f"Expired payment refund not economically viable: {refund_details['refund_amount']} {crypto_payment.coin_type} below threshold",
                            )
                            log.state_transition(
                                crypto_payment,
                                crypto_payment.status,
                                "LATEPAY_NOT_REFUNDED",
                                "economically unviable refund",
                            )
                            crypto_payment.status = (
                                CryptoPayment.STATUS_LATEPAY_NOT_REFUNDED
                            )
                            crypto_payment.refund_reason = f"Late payment - refund economically unviable ({refund_details['refund_amount']} {crypto_payment.coin_type})"
                            # Store the unviable refund amount for record keeping
                            crypto_payment.refund_amount = int(
                                refund_details["refund_amount"]
                                * coin_config["atomic_units"]
                            )

                            # Send refund email notification
                            if crypto_payment.invoice and crypto_payment.invoice.user:
                                try:
                                    # Create shop context request
                                    email_request = create_shop_context_request(
                                        env_request, crypto_payment
                                    )
                                    send_refund_email(
                                        email_request,
                                        crypto_payment.invoice.user.email,
                                        crypto_payment,
                                        refund_details,
                                    )
                                    log.payment_info(
                                        crypto_payment,
                                        "Sent refund email for economically unviable expired payment",
                                    )
                                except Exception as e:
                                    log.payment_error(
                                        crypto_payment,
                                        f"Failed to send refund email for economically unviable expired payment: {e}",
                                    )

                            # Delete invoice for terminal state
                            delete_invoice_for_terminal_state(
                                env_request.dbsession, crypto_payment
                            )
                            return  # Exit early - no refund to process

                        # Refund is viable - proceed with refund
                        log.refund_operation(
                            crypto_payment,
                            f"Expired payment eligible for refund: {refund_details}",
                        )

                        # Set status to expired-refunded immediately when refund is determined
                        crypto_payment.status = CryptoPayment.STATUS_LATEPAY_REFUNDED

                        result = payment_rescue.execute_refund(
                            refund_details, crypto_payment
                        )
                        if result["success"]:
                            log.refund_operation(
                                crypto_payment,
                                "Refund executed for expired payment",
                                tx_hash=result["tx_hash"],
                            )
                            # Track the customer refund
                            crypto_payment.refund_amount = int(
                                refund_details["refund_amount"]
                                * coin_config["atomic_units"]
                            )
                            crypto_payment.refund_tx_hash = result["tx_hash"]
                            crypto_payment.refund_reason = refund_details["reason"]

                            # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                            if not crypto_payment.swept_tx_hash:
                                # Calculate shop sweep amount: received - refund - fees
                                shop_sweep_amount = max(
                                    0,
                                    crypto_payment.received_amount
                                    - crypto_payment.refund_amount,
                                )

                                crypto_payment.swept_tx_hash = result["tx_hash"]
                                crypto_payment.swept_amount = shop_sweep_amount
                                crypto_payment.swept_timestamp = now_timestamp()

                            # Sweep restocking fee to shop owner
                            sweep_restocking_fee(
                                env_request.registry.settings,
                                crypto_payment,
                                refund_details,
                                env_request.dbsession,
                                "Expired payment",
                            )
                            # Status already set above

                            # Send refund email notification
                            if crypto_payment.invoice and crypto_payment.invoice.user:
                                try:
                                    send_refund_email(
                                        env_request,
                                        crypto_payment.invoice.user.email,
                                        crypto_payment,
                                        refund_details,
                                    )
                                    log.payment_info(
                                        crypto_payment,
                                        "Sent refund email for expired payment",
                                    )
                                except Exception as e:
                                    log.payment_error(
                                        crypto_payment,
                                        "Failed to send refund email for expired payment",
                                        e,
                                    )

                            # Commit the refund first
                            env_request.dbsession.add(crypto_payment)
                            env_request.dbsession.flush()

                            # Now sweep the remaining restocking fee to shop's wallet (AFTER refund)
                            fee_amount = int(
                                refund_details["fee_amount"]
                                * coin_config["atomic_units"]
                            )
                            if fee_amount > 0 and crypto_payment.shop_sweep_to_address:
                                try:
                                    # Small delay to ensure refund tx is processed
                                    time.sleep(2)

                                    if crypto_payment.coin_type == "XMR":
                                        # Sweep remaining balance from this specific subaddress only
                                        sweep_result = client._call(
                                            "sweep_all",
                                            {
                                                "account_index": crypto_payment.account_index,
                                                "subaddr_indices": [
                                                    crypto_payment.subaddress_index
                                                ],
                                                "address": crypto_payment.shop_sweep_to_address,
                                                "priority": 1,
                                                "get_tx_hex": True,
                                                "do_not_relay": False,
                                            },
                                        )
                                        fee_tx_hash = (
                                            sweep_result.get("tx_hash_list", [None])[0]
                                            if sweep_result.get("tx_hash_list")
                                            else None
                                        )
                                        # Get actual amount swept (whatever remained after refund, minus network fees)
                                        actual_swept = (
                                            sweep_result.get("amount_list", [0])[0]
                                            if sweep_result.get("amount_list")
                                            else 0
                                        )
                                    elif crypto_payment.coin_type == "DOGE":
                                        # Send exact restocking fee amount
                                        fee_crypto_amount = float(
                                            Decimal(fee_amount)
                                            / coin_config["atomic_units"]
                                        )
                                        fee_tx_hash = client._call(
                                            "sendtoaddress",
                                            [
                                                crypto_payment.shop_sweep_to_address,
                                                fee_crypto_amount,
                                            ],
                                        )
                                        actual_swept = fee_amount
                                    else:
                                        fee_tx_hash = None
                                        actual_swept = 0

                                    if fee_tx_hash and actual_swept > 0:
                                        crypto_payment.swept_amount = actual_swept
                                        crypto_payment.swept_tx_hash = fee_tx_hash
                                        crypto_payment.swept_timestamp = now_timestamp()
                                        log.sweep_operation(
                                            crypto_payment,
                                            f"Restocking fee swept: "
                                            f"{Decimal(actual_swept) / coin_config['atomic_units']} {crypto_payment.coin_type}",
                                            tx_hash=fee_tx_hash,
                                        )
                                except Exception as e:
                                    log.payment_error(
                                        crypto_payment,
                                        "Failed to sweep restocking fee",
                                        e,
                                    )
                        else:
                            log.payment_error(
                                crypto_payment,
                                f"Refund failed for expired payment: {result['error']}",
                            )
                elif payment_rescue:
                    # Payment rescue available but no refund address configured
                    log.payment_warning(
                        crypto_payment,
                        "Expired payment has no refund address configured - no refund possible",
                    )
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "LATEPAY_NOT_REFUNDED",
                        "no refund address",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_LATEPAY_NOT_REFUNDED
                    crypto_payment.refund_reason = (
                        "Expired payment - no refund address configured"
                    )
                    # Delete invoice for terminal state
                    delete_invoice_for_terminal_state(
                        env_request.dbsession, crypto_payment
                    )
        else:
            # No funds received after expiry - delete invoice for terminal expired state
            delete_invoice_for_terminal_state(env_request.dbsession, crypto_payment)
        return

    # Early check for confirmed payments that just need sweeping
    if (
        not incoming_transfers
        and crypto_payment.status == CryptoPayment.STATUS_CONFIRMED
        and client
        and crypto_payment.shop_sweep_to_address
        and not crypto_payment.is_swept
    ):
        log.payment_info(crypto_payment, "Confirmed payment needs sweep - processing")
        try:
            sweep_success = auto_sweep_payment(
                client, crypto_payment, env_request.dbsession
            )
            if sweep_success and crypto_payment.is_swept:
                log.payment_info(crypto_payment, "Swept successfully")
        except Exception as e:
            log.payment_error(
                crypto_payment, f"Auto-sweep failed for confirmed payment: {e}"
            )
        crypto_payment.updated_timestamp = now_ms
        env_request.dbsession.add(crypto_payment)
        return

    # Calculate transfer summary - even if empty
    if incoming_transfers:
        total_recv, txids, min_confs = summarize_txs(incoming_transfers)
    else:
        # No new transfers - use existing payment data
        total_recv = 0
        txids = []
        min_confs = 0

    # For duplicate detection, we need separate confirmation calculations

    # Existing seen txids
    try:
        existing = json.loads(crypto_payment.tx_hashes or "[]")
    except Exception:
        existing = []

    # Only count new amounts for txids we haven't seen yet to remain idempotent
    new_sum = 0
    seen = set(existing)
    total_fee = 0
    new_txids = []
    for t in incoming_transfers:
        txid = t.get("txid") or t.get("transaction_id")
        if txid and txid not in seen:
            new_sum += int(t.get("amount", 0) or 0)
            new_txids.append(txid)
            # Capture fee if available (some coins provide this, others don't)
            fee = t.get("fee", 0)
            if fee:
                total_fee += int(fee)

    # CRITICAL: If payment already received funds and we see NEW transactions,
    # these are duplicate payments that need separate tracking
    # ALSO detect multiple transactions during initial processing (pending status)
    is_duplicate_scenario = False
    if (
        crypto_payment.received_amount > 0
        and new_txids
        and crypto_payment.status != CryptoPayment.STATUS_PENDING
    ):
        # Case 1: Payment already processed, new transactions arrive
        is_duplicate_scenario = True
    elif crypto_payment.status == CryptoPayment.STATUS_PENDING and len(new_txids) > 1:
        # Case 2: Multiple transactions found during initial processing
        is_duplicate_scenario = True
        log.payment_error(
            crypto_payment,
            f"MULTIPLE TRANSACTIONS DETECTED during initial processing: "
            f"{len(new_txids)} transactions found. Will process first as payment, rest as duplicates.",
        )

    if is_duplicate_scenario:
        log.payment_error(
            crypto_payment,
            f"DUPLICATE PAYMENT DETECTED: {len(new_txids)} new transactions to {crypto_payment.status} payment "
            f"with existing balance {crypto_payment.received_amount}. Creating duplicate records for scanner to process.",
        )

        # Determine which transactions to create duplicates for
        if crypto_payment.status == CryptoPayment.STATUS_PENDING and len(new_txids) > 1:
            # For pending payments with multiple transactions:
            # Process FIRST transaction normally, rest as duplicates
            first_txid = new_txids[0]
            txids_to_duplicate = new_txids[1:]  # All except first become duplicates

            # Calculate sum of only the first transaction
            new_sum = 0
            for t in incoming_transfers:
                txid = t.get("txid") or t.get("transaction_id")
                if txid == first_txid:
                    new_sum += int(t.get("amount", 0) or 0)
                    break

            # Only keep the first txid
            new_txids = [first_txid]
            log.payment_info(
                crypto_payment,
                f"Processing first transaction '{first_txid}' as payment, "
                f"treating {len(txids_to_duplicate)} others as duplicates: {txids_to_duplicate}",
            )
        else:
            # For already-processed payments with new transactions:
            # All new transactions are duplicates
            txids_to_duplicate = new_txids
            # Set new_sum to 0 since all new transactions are duplicates
            new_sum = 0
            new_txids = []  # Don't add any txids to the original payment

        # Create separate payment records for each duplicate transaction
        # But DON'T process refunds here - let the scanner handle that
        for txid in txids_to_duplicate:
            # Check if duplicate record already exists for this specific transaction ID
            # This prevents creating multiple duplicate records for the same txid (recursive bug)
            # but allows different txids to create separate duplicate records (triple-pay support)
            #
            # Query both doublepay-refund and doublepay-refund-complete statuses:
            # - doublepay-refund: Currently being processed
            # - doublepay-refund-complete: Already refunded (prevents recreation)
            # Optimize duplicate search: only check same coin type and address/subaddress
            if crypto_payment.coin_type == "XMR":
                # For XMR, filter by account and subaddress indices
                duplicate_candidates = (
                    env_request.dbsession.query(CryptoPayment)
                    .filter(
                        CryptoPayment.coin_type == crypto_payment.coin_type,
                        CryptoPayment.account_index == crypto_payment.account_index,
                        CryptoPayment.subaddress_index
                        == crypto_payment.subaddress_index,
                        CryptoPayment.status.in_(
                            [
                                CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                                CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
                            ]
                        ),
                    )
                    .all()
                )
            else:
                # For DOGE/BTC-like coins, filter by address
                duplicate_candidates = (
                    env_request.dbsession.query(CryptoPayment)
                    .filter(
                        CryptoPayment.coin_type == crypto_payment.coin_type,
                        CryptoPayment.address == crypto_payment.address,
                        CryptoPayment.status.in_(
                            [
                                CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                                CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
                            ]
                        ),
                    )
                    .all()
                )

            log.payment_info(
                crypto_payment,
                f"Checking for existing duplicates of transaction {txid}: found {len(duplicate_candidates)} doublepay-refund records to examine",
            )

            existing_duplicate = None
            for candidate in duplicate_candidates:
                try:
                    candidate_txids = json.loads(candidate.tx_hashes or "[]")
                    log.payment_debug(
                        candidate, f"Candidate has tx_hashes: {candidate_txids}"
                    )
                    if txid in candidate_txids:
                        existing_duplicate = candidate
                        log.payment_info(
                            crypto_payment,
                            f"Found existing duplicate record {candidate.id} for transaction {txid}",
                        )
                        break
                except (json.JSONDecodeError, TypeError) as e:
                    log.payment_warning(candidate, f"Failed to parse tx_hashes: {e}")
                    continue

            if existing_duplicate:
                log.payment_info(
                    crypto_payment,
                    f"Skipping duplicate creation - record already exists for transaction {txid}: {existing_duplicate.id}",
                )
                continue
            else:
                log.payment_info(
                    crypto_payment,
                    f"No existing duplicate found for transaction {txid}, creating new record",
                )

            # Find the transaction data for this txid
            duplicate_tx = None
            for tx in incoming_transfers:
                if tx.get("txid") == txid:
                    duplicate_tx = tx
                    break

            if duplicate_tx:
                # Create separate duplicate payment record
                duplicate_payment = _create_duplicate_payment(
                    crypto_payment,
                    duplicate_tx,
                    crypto_payment.coin_type,
                    env_request.dbsession,
                )
                env_request.dbsession.add(duplicate_payment)
                env_request.dbsession.flush()

                log.payment_info(
                    duplicate_payment,
                    f"Created duplicate payment record for transaction {txid} "
                    f"with amount {duplicate_payment.received_amount} {crypto_payment.coin_type} - scanner will handle refund",
                )

    # Note: No recalculation needed - new_sum and new_txids are already set correctly
    # based on the duplicate detection logic above

    # Update tx_hashes with new transactions (but not received_amount yet)
    merged = list(dict.fromkeys(list(existing) + new_txids))
    crypto_payment.tx_hashes = json.dumps(merged)

    # Update confirmations from only legitimate (existing) transactions, not duplicates
    legitimate_transfers = []
    seen = set(existing)
    for tx in incoming_transfers:
        txid = tx.get("txid") or tx.get("transaction_id")
        if txid and txid in seen:
            legitimate_transfers.append(tx)

    if legitimate_transfers:
        _, _, legitimate_min_confs = summarize_txs(legitimate_transfers)
        crypto_payment.current_confirmations = legitimate_min_confs
    else:
        crypto_payment.current_confirmations = min_confs

    crypto_payment.updated_timestamp = now_ms

    # Update received_amount with new_sum before status checks
    crypto_payment.received_amount = (crypto_payment.received_amount or 0) + new_sum

    # Update status from pending to received if this is the first amount received
    if crypto_payment.status == CryptoPayment.STATUS_PENDING and new_sum > 0:
        log.state_transition(
            crypto_payment,
            "PENDING",
            "RECEIVED",
            f"amount {crypto_payment.received_amount}",
        )
        crypto_payment.status = CryptoPayment.STATUS_RECEIVED

    # Check if original payment should move to confirmed status
    if (
        crypto_payment.received_amount >= crypto_payment.expected_amount
        and crypto_payment.current_confirmations
        >= int(crypto_payment.confirmations_required)
        and crypto_payment.status == CryptoPayment.STATUS_RECEIVED
    ):
        # ALWAYS finalize invoice when payment moves to confirmed
        if crypto_payment.invoice:
            log.payment_info(
                crypto_payment,
                f"Payment confirmed, finalizing invoice {crypto_payment.invoice.id}",
            )
            finalize_invoice(env_request, crypto_payment, send_emails=True)

        # Update status to confirmed
        if crypto_payment.received_amount > crypto_payment.expected_amount:
            log.state_transition(
                crypto_payment,
                "RECEIVED",
                "CONFIRMED_OVERPAY",
                f"received {crypto_payment.received_amount}, expected {crypto_payment.expected_amount}",
            )
            crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_OVERPAY
        else:
            log.state_transition(
                crypto_payment,
                "RECEIVED",
                "CONFIRMED",
                f"{crypto_payment.current_confirmations} confirmations",
            )
            crypto_payment.status = CryptoPayment.STATUS_CONFIRMED

        # Send confirmation emails if not already sent (independent of invoice finalization)
        if crypto_payment.invoice and crypto_payment.invoice.user:
            # Create a request wrapper with shop's domain context for emails
            email_request = create_shop_context_request(env_request, crypto_payment)

            # Send purchase confirmation email if not already sent
            if not crypto_payment.purchase_email_sent:
                try:
                    send_purchase_email(
                        email_request,
                        crypto_payment.invoice.user.email,
                        [item.product for item in crypto_payment.invoice.line_items],
                        crypto_payment.invoice.total,
                    )
                    crypto_payment.purchase_email_sent = True
                    log.payment_info(crypto_payment, "Purchase confirmation email sent")
                except Exception as e:
                    log.payment_error(
                        crypto_payment, f"Failed to send purchase email: {e}"
                    )

            # Send sales notification email if not already sent
            if not crypto_payment.sales_email_sent:
                try:
                    send_sale_email(
                        email_request,
                        crypto_payment.invoice.shop,
                        [item.product for item in crypto_payment.invoice.line_items],
                        crypto_payment.invoice.total,
                    )
                    crypto_payment.sales_email_sent = True
                    log.payment_info(crypto_payment, "Sales notification email sent")
                except Exception as e:
                    log.payment_error(
                        crypto_payment, f"Failed to send sales email: {e}"
                    )

        # ALSO handle already-confirmed payments that go through duplicate detection path
        # (They need emails and sweep processing too)
        elif (
            crypto_payment.status == CryptoPayment.STATUS_CONFIRMED
            and crypto_payment.invoice
        ):
            # Send confirmation emails if not already sent for confirmed payments
            email_request = create_shop_context_request(env_request, crypto_payment)

            # Send purchase confirmation email if not already sent
            if not crypto_payment.purchase_email_sent:
                try:
                    send_purchase_email(
                        email_request,
                        crypto_payment.invoice.user.email,
                        [item.product for item in crypto_payment.invoice.line_items],
                        crypto_payment.invoice.total,
                    )
                    crypto_payment.purchase_email_sent = True
                    log.payment_info(
                        crypto_payment,
                        "Purchase confirmation email sent for confirmed payment",
                    )
                except Exception as e:
                    log.payment_error(
                        crypto_payment,
                        f"Failed to send purchase email for confirmed payment: {e}",
                    )

            # Send sales notification email if not already sent
            if not crypto_payment.sales_email_sent:
                try:
                    send_sale_email(
                        email_request,
                        crypto_payment.invoice.shop,
                        [item.product for item in crypto_payment.invoice.line_items],
                        crypto_payment.invoice.total,
                    )
                    crypto_payment.sales_email_sent = True
                    log.payment_info(
                        crypto_payment,
                        "Sales notification email sent for confirmed payment",
                    )
                except Exception as e:
                    log.payment_error(
                        crypto_payment,
                        f"Failed to send sales email for confirmed payment: {e}",
                    )

        # Auto-sweep confirmed payments that haven't been swept yet
        if (
            client
            and crypto_payment.status == CryptoPayment.STATUS_CONFIRMED
            and crypto_payment.shop_sweep_to_address
            and not crypto_payment.is_swept
        ):
            log.payment_info(crypto_payment, "Confirmed - attempting sweep")
            try:
                sweep_success = auto_sweep_payment(
                    client, crypto_payment, env_request.dbsession
                )
                if sweep_success and crypto_payment.is_swept:
                    log.payment_info(crypto_payment, "Swept successfully")
            except Exception as e:
                log.payment_error(
                    crypto_payment, f"Auto-sweep failed for confirmed payment: {e}"
                )

        env_request.dbsession.add(crypto_payment)
        return

    # Normal case: track customer's network fee if available
    # (received_amount was already updated above)
    if total_fee > 0:
        crypto_payment.received_network_fee = total_fee

    # Merge and dedupe txids
    merged = list(dict.fromkeys(list(existing) + txids))
    crypto_payment.tx_hashes = json.dumps(merged)

    # Update current confirmation count
    crypto_payment.current_confirmations = min_confs
    crypto_payment.updated_timestamp = now_ms

    # Status logic
    if (
        crypto_payment.received_amount >= crypto_payment.expected_amount
        and min_confs >= int(crypto_payment.confirmations_required)
    ):
        # Check if invoice needs finalization (products not unlocked yet)
        invoice_needs_finalization = False
        if crypto_payment.invoice and crypto_payment.invoice.line_items:
            # Check if any products are still locked for this user
            for line_item in crypto_payment.invoice.line_items:
                if (
                    line_item.product.get_userproduct_for_user(
                        crypto_payment.invoice.user
                    )
                    is None
                ):
                    invoice_needs_finalization = True
                    break

        # Use new organized payment confirmation flow with proper order of operations
        if crypto_payment.status != CryptoPayment.STATUS_CONFIRMED:
            # Process confirmed payment with proper order: finalize → refund → sweep
            process_results = process_confirmed_payment(
                env_request, crypto_payment, client, payment_rescue
            )

            if process_results:
                # Safe extraction of nested values
                overpay_refund = process_results.get("overpayment_refund") or {}
                auto_sweep = process_results.get("auto_sweep") or {}

                log.payment_info(
                    crypto_payment,
                    f"Payment confirmation results: "
                    f"finalized={process_results.get('invoice_finalized', False)}, "
                    f"overpay_refund={overpay_refund.get('success', 'N/A')}, "
                    f"restocking_swept={process_results.get('restocking_fee_swept', False)}, "
                    f"auto_sweep={auto_sweep.get('success', 'N/A')}",
                )
            else:
                log.payment_error(
                    crypto_payment, "Payment confirmation failed - no results returned"
                )
        elif invoice_needs_finalization:
            # Handle stuck confirmed payments that were never finalized
            log.payment_error(
                crypto_payment,
                "Payment is confirmed but invoice not finalized - finalizing now",
            )
            finalize_invoice(env_request, crypto_payment, send_emails=False)
    else:
        # Early detection - as soon as we receive ANY funds, determine the refund scenario
        # This gets payments out of the active processing queue immediately
        if crypto_payment.received_amount > 0:
            # Calculate confirmations for early detection
            if incoming_transfers:
                _, _, early_min_confs = summarize_txs(incoming_transfers)
            else:
                early_min_confs = 0

            # Check for underpayment first (most common case)
            # Since we don't allow multiple transactions, use only new_sum for comparison
            coin_config = get_coin_config(crypto_payment.coin_type)
            atomic_units = coin_config["atomic_units"]

            # Ensure integer comparison to avoid float precision issues
            new_sum_int = int(new_sum)
            expected_amount_int = int(crypto_payment.expected_amount)
            received_amount_int = int(crypto_payment.received_amount)

            # Log for debugging
            log.payment_info(
                crypto_payment,
                f"Amount check ({crypto_payment.coin_type}): "
                f"new_sum={new_sum_int} ({new_sum_int/atomic_units:.12f} {crypto_payment.coin_type}), "
                f"expected_amount={expected_amount_int} ({expected_amount_int/atomic_units:.12f} {crypto_payment.coin_type}), "
                f"received_amount={received_amount_int} ({received_amount_int/atomic_units:.12f} {crypto_payment.coin_type}), "
                f"status={crypto_payment.status}, "
                f"early_min_confs={early_min_confs}",
            )

            # For first payment, use new_sum directly since we don't allow multiple payments
            # Also check existing received payments that haven't been evaluated yet
            if (
                payment_rescue
                and crypto_payment.invoice
                and crypto_payment.invoice.user
                and crypto_payment.status
                == CryptoPayment.STATUS_RECEIVED  # Only check received status
                and received_amount_int
                < expected_amount_int  # Check current received amount
                and early_min_confs
                >= int(
                    crypto_payment.confirmations_required
                )  # Wait for required confirmations
            ):
                # Underpayment detected - mark for refund after required confirmations
                coin_config = get_coin_config(crypto_payment.coin_type)
                atomic_units = coin_config["atomic_units"]
                # Use received_amount for the actual amount received
                received_xmr = Decimal(received_amount_int) / atomic_units
                expected_xmr = Decimal(crypto_payment.expected_amount) / atomic_units

                log.payment_info(
                    crypto_payment,
                    f"EARLY DETECTION - Underpayment: "
                    f"received {received_xmr} {crypto_payment.coin_type}, expected {expected_xmr} {crypto_payment.coin_type} "
                    f"({early_min_confs}/{crypto_payment.confirmations_required} confirmations) - marking for refund",
                )

                # Check if refund address is available
                if crypto_payment.refund_address:
                    # Set status immediately to get out of active queue
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "UNDERPAID_REFUNDED",
                        f"received {received_xmr}, expected {expected_xmr}",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_UNDERPAID_REFUNDED
                    crypto_payment.refund_reason = f"Underpayment: received {received_xmr} but expected {expected_xmr}"

                    # Try refund if we have enough confirmations, otherwise wait
                    if early_min_confs >= int(crypto_payment.confirmations_required):
                        refund_details = payment_rescue.handle_underpayment(
                            crypto_payment,
                            expected_xmr,
                            received_xmr,
                            crypto_payment.invoice.user,
                        )

                        if refund_details:
                            # Check if refund is economically viable
                            if not refund_details.get("economically_viable", True):
                                # Refund is not economically viable - transition to not-refunded state
                                log.payment_info(
                                    crypto_payment,
                                    f"Refund not economically viable: {refund_details['refund_amount']} {crypto_payment.coin_type} below threshold",
                                )
                                log.state_transition(
                                    crypto_payment,
                                    crypto_payment.status,
                                    "UNDERPAID_NOT_REFUNDED",
                                    "economically unviable refund",
                                )
                                crypto_payment.status = (
                                    CryptoPayment.STATUS_UNDERPAID_NOT_REFUNDED
                                )
                                crypto_payment.refund_reason = f"Underpayment - refund economically unviable ({refund_details['refund_amount']} {crypto_payment.coin_type})"
                                # Store the unviable refund amount for record keeping
                                crypto_payment.refund_amount = int(
                                    refund_details["refund_amount"]
                                    * coin_config["atomic_units"]
                                )

                                # Send refund email notification
                                if (
                                    crypto_payment.invoice
                                    and crypto_payment.invoice.user
                                ):
                                    try:
                                        # Create shop context request
                                        email_request = create_shop_context_request(
                                            env_request, crypto_payment
                                        )
                                        send_refund_email(
                                            email_request,
                                            crypto_payment.invoice.user.email,
                                            crypto_payment,
                                            refund_details,
                                        )
                                        log.payment_info(
                                            crypto_payment,
                                            "Sent refund email for economically unviable underpayment",
                                        )
                                    except Exception as e:
                                        log.payment_error(
                                            crypto_payment,
                                            f"Failed to send refund email for economically unviable underpayment: {e}",
                                        )

                                # Delete invoice for terminal state
                                delete_invoice_for_terminal_state(
                                    env_request.dbsession, crypto_payment
                                )
                            else:
                                # Refund is viable - proceed with refund
                                result = payment_rescue.execute_refund(
                                    refund_details, crypto_payment
                                )
                                if result["success"]:
                                    log.payment_info(
                                        crypto_payment,
                                        f"Refund executed for underpayment: TX {result['tx_hash']}",
                                    )
                                    # Track the refund details
                                    crypto_payment.refund_amount = int(
                                        refund_details["refund_amount"]
                                        * coin_config["atomic_units"]
                                    )
                                    crypto_payment.refund_tx_hash = result["tx_hash"]
                                    crypto_payment.refund_reason = refund_details[
                                        "reason"
                                    ]

                                    # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                                    if not crypto_payment.swept_tx_hash:
                                        # Calculate shop sweep amount: received - refund - fees
                                        shop_sweep_amount = max(
                                            0,
                                            crypto_payment.received_amount
                                            - crypto_payment.refund_amount,
                                        )

                                        crypto_payment.swept_tx_hash = result["tx_hash"]
                                        crypto_payment.swept_amount = shop_sweep_amount
                                        crypto_payment.swept_timestamp = now_timestamp()

                                    # Commit the refund first
                                    env_request.dbsession.add(crypto_payment)
                                    env_request.dbsession.flush()

                                    # Sweep restocking fee to shop owner
                                    sweep_restocking_fee(
                                        env_request.registry.settings,
                                        crypto_payment,
                                        refund_details,
                                        env_request.dbsession,
                                        "Underpayment",
                                    )
                                else:
                                    log.payment_error(
                                        crypto_payment,
                                        f"Refund failed for underpayment: {result['error']}",
                                    )
                else:
                    # No refund possible - no refund address configured
                    log.payment_error(
                        crypto_payment,
                        "Underpayment has no refund address configured - marking as no-refund",
                    )
                    log.state_transition(
                        crypto_payment,
                        crypto_payment.status,
                        "UNDERPAID_NOT_REFUNDED",
                        "no refund address",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_UNDERPAID_NOT_REFUNDED
                    crypto_payment.refund_reason = (
                        "Underpayment - no refund address configured"
                    )
                    # Delete invoice for terminal state
                    delete_invoice_for_terminal_state(
                        env_request.dbsession, crypto_payment
                    )

            # Check if received payment has enough confirmations to become confirmed
            elif (
                crypto_payment.status == CryptoPayment.STATUS_RECEIVED
                and received_amount_int >= expected_amount_int  # Has enough amount
                and early_min_confs
                >= int(
                    crypto_payment.confirmations_required
                )  # Has enough confirmations
            ):
                # Check for exact payment first
                if received_amount_int == expected_amount_int:
                    log.payment_info(
                        crypto_payment,
                        f"Exact payment confirmed with {early_min_confs}/{crypto_payment.confirmations_required} confirmations",
                    )
                    crypto_payment.status = CryptoPayment.STATUS_CONFIRMED
                    finalize_invoice(env_request, crypto_payment, send_emails=True)
                # EARLY DETECTION: Check for overpayments on existing received payments
                elif (
                    payment_rescue
                    and crypto_payment.invoice
                    and crypto_payment.invoice.user
                    and received_amount_int > expected_amount_int  # Overpayment
                ):
                    # Overpayment detected - check if it exceeds threshold
                    coin_config = get_coin_config(crypto_payment.coin_type)
                    atomic_units = coin_config["atomic_units"]
                    received_crypto = Decimal(received_amount_int) / atomic_units
                    expected_crypto = Decimal(expected_amount_int) / atomic_units

                    log.payment_info(
                        crypto_payment,
                        f"EARLY DETECTION - Potential overpayment: "
                        f"received {received_crypto} {crypto_payment.coin_type}, expected {expected_crypto} {crypto_payment.coin_type} "
                        f"({early_min_confs}/{crypto_payment.confirmations_required} confirmations) - checking threshold",
                    )

                    # Check if overpayment exceeds 5% threshold using PaymentRescue logic
                    refund_details = payment_rescue.handle_overpayment(
                        crypto_payment,
                        expected_crypto,
                        received_crypto,
                        crypto_payment.invoice.user,
                    )

                    if refund_details:
                        # Overpayment exceeds threshold - process refund
                        log.payment_info(
                            crypto_payment,
                            f"EARLY DETECTION - Overpayment threshold exceeded: {refund_details}",
                        )

                        # Mark as confirmed with overpayment detected (refund pending)
                        crypto_payment.status = CryptoPayment.STATUS_CONFIRMED_OVERPAY
                        crypto_payment.refund_reason = refund_details["reason"]

                        # Try refund immediately since we have enough confirmations
                        result = payment_rescue.execute_refund(
                            refund_details, crypto_payment
                        )
                        if result["success"]:
                            log.payment_info(
                                crypto_payment,
                                f"Excess refunded: TX {result['tx_hash']}",
                            )
                            # Mark as confirmed with overpayment refunded
                            crypto_payment.status = (
                                CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED
                            )
                            crypto_payment.refund_tx_hash = result["tx_hash"]

                            # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                            if not crypto_payment.swept_tx_hash:
                                # Calculate shop sweep amount: received - refund - fees
                                shop_sweep_amount = max(
                                    0,
                                    crypto_payment.received_amount
                                    - crypto_payment.refund_amount,
                                )

                                crypto_payment.swept_tx_hash = result["tx_hash"]
                                crypto_payment.swept_amount = shop_sweep_amount
                                crypto_payment.swept_timestamp = now_timestamp()
                            crypto_payment.refund_confirmations = 0  # Just sent

                            # Finalize invoice since core payment amount is sufficient
                            finalize_invoice(
                                env_request, crypto_payment, send_emails=True
                            )

                            # Note: Restocking fee will be swept when refund is fully confirmed
                            # to avoid double-sweeping before refund transaction is safely confirmed
                        else:
                            log.payment_error(
                                crypto_payment,
                                f"Refund failed for overpayment: {result['error']}",
                            )
                    else:
                        # Overpayment within acceptable threshold - just confirm normally
                        log.payment_info(
                            crypto_payment,
                            "EARLY DETECTION - Overpayment within 5% threshold - confirming normally",
                        )
                        crypto_payment.status = CryptoPayment.STATUS_CONFIRMED
                        finalize_invoice(env_request, crypto_payment, send_emails=True)

            # Check for overpayment (exact match or overpaid) - for first payment
            elif (
                new_sum_int >= expected_amount_int
                and crypto_payment.status != CryptoPayment.STATUS_RECEIVED
                and crypto_payment.received_amount == 0  # First payment check
            ):
                crypto_payment.status = CryptoPayment.STATUS_RECEIVED

                # If this will become confirmed, check for overpayment scenario immediately
                if early_min_confs >= int(crypto_payment.confirmations_required):
                    # Already confirmed logic will handle this below
                    pass
                else:
                    # Just received, check if it's an overpayment for early detection
                    if new_sum_int > expected_amount_int:
                        coin_config = get_coin_config(crypto_payment.coin_type)
                        atomic_units = coin_config["atomic_units"]
                        received_xmr = Decimal(new_sum_int) / atomic_units
                        expected_xmr = (
                            Decimal(crypto_payment.expected_amount) / atomic_units
                        )

                        log.payment_info(
                            crypto_payment,
                            f"EARLY DETECTION - Overpayment: "
                            f"received {received_xmr} {crypto_payment.coin_type}, expected {expected_xmr} {crypto_payment.coin_type} "
                            f"({early_min_confs}/{crypto_payment.confirmations_required} confirmations) - will refund excess when confirmed",
                        )

            # Legacy case - payment needs to be marked as received (but don't downgrade confirmed)
            elif (
                crypto_payment.status == CryptoPayment.STATUS_PENDING
                and crypto_payment.received_amount > 0
            ):
                crypto_payment.status = CryptoPayment.STATUS_RECEIVED

    # Note: Auto-sweep is now handled immediately when payment is confirmed (based on RPC confirmation data)

    # Check if this confirmed payment needs sweeping (handles case where payment was already confirmed)
    if (
        client
        and crypto_payment.status == CryptoPayment.STATUS_CONFIRMED
        and crypto_payment.shop_sweep_to_address
        and not crypto_payment.is_swept
    ):
        log.payment_info(crypto_payment, "Confirmed payment needs sweep - attempting")
        try:
            sweep_success = auto_sweep_payment(
                client, crypto_payment, env_request.dbsession
            )
            if sweep_success and crypto_payment.is_swept:
                log.payment_info(crypto_payment, "Swept successfully")
        except Exception as e:
            log.payment_error(
                crypto_payment, f"Auto-sweep failed for confirmed payment: {e}"
            )

    env_request.dbsession.add(crypto_payment)


def process_refund_confirmations(request, settings):
    """
    Monitor refund transactions for confirmation status.
    Updates refund_confirmations and transitions status when fully confirmed.
    """
    log.processing_cycle("Starting refund confirmation monitoring")

    db = request.dbsession

    # Query payments that need refund confirmation monitoring OR retry
    refund_queue = (
        db.query(CryptoPayment)
        .options(
            sa.orm.joinedload(CryptoPayment.user),
            sa.orm.joinedload(CryptoPayment.shop),
        )
        .filter(
            CryptoPayment.status.in_(
                [
                    CryptoPayment.STATUS_LATEPAY_REFUNDED,
                    CryptoPayment.STATUS_UNDERPAID_REFUNDED,
                    CryptoPayment.STATUS_CONFIRMED_OVERPAY,  # Still pending refund confirmation
                    CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED,  # Refund sent, awaiting confirmation
                    CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED,
                ]
            ),
        )
        .all()
    )

    if not refund_queue:
        log.processing_cycle("No refund transactions need confirmation monitoring")
        return

    log.processing_cycle("Found refund transactions to monitor", len(refund_queue))

    # Group by coin type to get appropriate clients
    refunds_by_coin = {}
    for payment in refund_queue:
        coin_type = payment.coin_type
        if coin_type not in refunds_by_coin:
            refunds_by_coin[coin_type] = []
        refunds_by_coin[coin_type].append(payment)

    # Process each coin type
    for coin_type, coin_refunds in refunds_by_coin.items():
        log.processing_cycle(
            f"Monitoring {coin_type} refund transactions", len(coin_refunds)
        )

        try:
            client = get_crypto_client(settings, coin_type)
        except ValueError as e:
            log.error_with_context(
                f"Failed to get {coin_type} client for refund monitoring", e
            )
            continue

        for payment in coin_refunds:
            try:
                # Check if this is a payment that needs refund retry (no refund_tx_hash yet)
                if not payment.refund_tx_hash:
                    log.payment_debug(payment, "Checking if refund can be retried")

                    # Check if incoming payment now has enough confirmations for refund retry
                    coin_config = get_coin_config(payment.coin_type)
                    required_confirmations = coin_config.get(
                        "confirmations_required", 10
                    )  # Default to 10 if not specified
                    if payment.current_confirmations >= required_confirmations:
                        log.payment_info(
                            payment,
                            f"Retrying refund - now has {payment.current_confirmations} confirmations",
                        )

                        # Retry the refund process (import payment rescue here to avoid circular imports)
                        from .crypto_payment_rescue import PaymentRescue

                        # Get the correct client for this payment's coin type
                        coin_specific_client = get_crypto_client(
                            request.registry.settings, payment.coin_type
                        )
                        payment_rescue = PaymentRescue(
                            request.dbsession, coin_specific_client
                        )

                        # Determine refund type and retry
                        if payment.status == CryptoPayment.STATUS_UNDERPAID_REFUNDED:
                            # This was already marked as refunded but refund failed due to confirmations
                            coin_config = get_coin_config(payment.coin_type)
                            atomic_units = coin_config["atomic_units"]
                            expected_amount = (
                                Decimal(payment.expected_amount) / atomic_units
                            )
                            received_amount = (
                                Decimal(payment.received_amount) / atomic_units
                            )

                            refund_details = payment_rescue.handle_underpayment(
                                payment, expected_amount, received_amount, payment.user
                            )
                            if refund_details:
                                # Check if refund is economically viable
                                if not refund_details.get("economically_viable", True):
                                    # Transition to not-refunded state
                                    log.payment_info(
                                        payment,
                                        f"Refund not economically viable: {refund_details['refund_amount']} {payment.coin_type} below threshold",
                                    )
                                    payment.validate_and_set_status(
                                        CryptoPayment.STATUS_UNDERPAID_NOT_REFUNDED,
                                        "economically unviable refund",
                                    )
                                    payment.refund_reason = f"Underpayment - refund economically unviable ({refund_details['refund_amount']} {payment.coin_type})"

                                    # Send refund email notification
                                    if payment.invoice and payment.invoice.user:
                                        try:
                                            # Create shop context request
                                            email_request = create_shop_context_request(
                                                request, payment
                                            )
                                            send_refund_email(
                                                email_request,
                                                payment.invoice.user.email,
                                                payment,
                                                refund_details,
                                            )
                                            log.payment_info(
                                                payment,
                                                "Sent refund email for economically unviable underpayment (passive monitoring)",
                                            )
                                        except Exception as e:
                                            log.payment_error(
                                                payment,
                                                f"Failed to send refund email for economically unviable underpayment (passive monitoring): {e}",
                                            )

                                    db.add(payment)
                                    continue

                                result = payment_rescue.execute_refund(
                                    refund_details, payment
                                )
                                if result["success"]:
                                    payment.refund_tx_hash = result["tx_hash"]
                                    payment.refund_amount = int(
                                        refund_details["refund_amount"] * atomic_units
                                    )

                                    # CRITICAL FIX: Multi-output refund transactions also sweep funds to shop
                                    if not payment.swept_tx_hash:
                                        # Calculate shop sweep amount: received - refund - fees
                                        shop_sweep_amount = max(
                                            0,
                                            payment.received_amount
                                            - payment.refund_amount,
                                        )

                                        payment.swept_tx_hash = result["tx_hash"]
                                        payment.swept_amount = shop_sweep_amount
                                        payment.swept_timestamp = now_timestamp()
                                    db.add(payment)  # Mark for database commit
                                    log.payment_info(
                                        payment,
                                        f"REFUND RETRY SUCCESSFUL: TX {result['tx_hash']} (incoming payment now has {payment.current_confirmations} confirmations)",
                                    )

                                    # Commit the refund first
                                    db.flush()

                                    # Sweep restocking fee to shop owner
                                    sweep_restocking_fee(
                                        request.registry.settings,
                                        payment,
                                        refund_details,
                                        db,
                                        "Refund retry",
                                    )
                    continue

                log.payment_debug(
                    payment,
                    f"Checking REFUND transaction confirmations (TX: {payment.refund_tx_hash[:16]}..., current refund confirmations: {payment.refund_confirmations})",
                )

                # Check transaction confirmation status
                if coin_type == "XMR":
                    confirmations = get_monero_tx_confirmations(
                        client, payment.refund_tx_hash, payment.account_index
                    )
                elif coin_type == "DOGE":
                    confirmations = get_dogecoin_tx_confirmations(
                        client, payment.refund_tx_hash
                    )
                else:
                    log.payment_error(
                        payment,
                        f"Unsupported coin type for refund monitoring: {coin_type}",
                    )
                    continue

                # Update confirmation count
                old_confirmations = payment.refund_confirmations
                payment.refund_confirmations = confirmations

                if confirmations != old_confirmations:
                    log.confirmation_update(payment, old_confirmations, confirmations)

                # Check if refund is now fully confirmed based on coin type requirements
                required_confirmations = OUTBOUND_CONFIRMATIONS_REQUIRED.get(
                    coin_type, 10
                )

                if confirmations >= required_confirmations:
                    old_status = payment.status

                    # Transition to final refunded status
                    if payment.status == CryptoPayment.STATUS_CONFIRMED_OVERPAY:
                        payment.status = (
                            CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE
                        )
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                        # Sweep remaining funds (restocking fee) to shop
                        sweep_restocking_fee(
                            request.registry.settings,
                            payment,
                            {"fee_amount": 0.09},  # 9% fee placeholder
                            db,
                            "Confirmed overpayment",
                        )
                    elif (
                        payment.status
                        == CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED
                    ):
                        payment.status = (
                            CryptoPayment.STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE
                        )
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                        # Sweep remaining funds (restocking fee) to shop
                        sweep_restocking_fee(
                            request.registry.settings,
                            payment,
                            {"fee_amount": 0.09},  # 9% fee placeholder
                            db,
                            "Confirmed overpayment refund",
                        )
                    elif payment.status == CryptoPayment.STATUS_LATEPAY_REFUNDED:
                        payment.status = CryptoPayment.STATUS_LATEPAY_REFUNDED_COMPLETE
                        # Delete invoice for terminal state
                        delete_invoice_for_terminal_state(db, payment)
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                        # Sweep remaining funds (restocking fee) to shop
                        sweep_restocking_fee(
                            request.registry.settings,
                            payment,
                            {"fee_amount": 0.09},  # 9% fee placeholder
                            db,
                            "Confirmed expired payment",
                        )
                    elif payment.status == CryptoPayment.STATUS_UNDERPAID_REFUNDED:
                        payment.status = (
                            CryptoPayment.STATUS_UNDERPAID_REFUNDED_COMPLETE
                        )
                        # Delete invoice for terminal state
                        delete_invoice_for_terminal_state(db, payment)
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                        # Sweep remaining funds (restocking fee) to shop
                        sweep_restocking_fee(
                            request.registry.settings,
                            payment,
                            {"fee_amount": 0.09},  # 9% fee placeholder
                            db,
                            "Confirmed underpayment",
                        )
                    elif payment.status == CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED:
                        payment.status = (
                            CryptoPayment.STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE
                        )
                        # Delete invoice for terminal state
                        delete_invoice_for_terminal_state(db, payment)
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                    elif payment.status == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED:
                        payment.status = (
                            CryptoPayment.STATUS_DOUBLEPAY_REFUNDED_COMPLETE
                        )
                        # No invoice to delete - duplicate payments don't have invoices
                        log.state_transition(
                            payment,
                            old_status,
                            payment.status,
                            f"refund confirmed with {confirmations} confirmations",
                        )
                        # Sweep remaining funds (restocking fee) to shop
                        sweep_restocking_fee(
                            request.registry.settings,
                            payment,
                            {"fee_amount": 0.09},  # 9% fee placeholder
                            db,
                            "Confirmed duplicate payment",
                        )
                    else:
                        # Fallback for any other status
                        log.payment_info(
                            payment,
                            f"Refund fully confirmed (status: {payment.status})",
                        )

                # Update timestamp
                payment.updated_timestamp = int(time.time() * 1000)
                db.add(payment)

            except Exception as e:
                log.payment_error(payment, "Failed to check refund confirmations", e)
                continue


def get_monero_tx_confirmations(client, tx_hash, account_index):
    """Get confirmation count for a Monero transaction."""
    try:
        # Use get_transfer_by_txid to get transaction details
        result = client._call(
            "get_transfer_by_txid", {"txid": tx_hash, "account_index": account_index}
        )
        if result and "transfer" in result:
            return result["transfer"].get("confirmations", 0)
        return 0
    except Exception as e:
        log.processing_cycle(
            f"Could not get Monero TX confirmations for {tx_hash}: {e}"
        )
        return 0


def get_dogecoin_tx_confirmations(client, tx_hash):
    """Get confirmation count for a Dogecoin transaction."""
    try:
        result = client.gettransaction(tx_hash)
        return result.get("confirmations", 0)
    except Exception as e:
        log.processing_cycle(
            f"Could not get Dogecoin TX confirmations for {tx_hash}: {e}"
        )
        return 0


def update_payment_confirmations_only(client, crypto_payment, coin_type):
    """
    Update confirmation count for refund-pending payments without full processing.
    This ensures refunds can be retried once incoming payments have 10+ confirmations.
    """
    try:
        if coin_type == "XMR":
            # Query transfers for the payment subaddress
            res = (
                client.get_transfers_for_subaddr(
                    crypto_payment.account_index,
                    [crypto_payment.subaddress_index],
                )
                or {}
            )
            incoming = res.get("in", []) or []

            # For duplicate payments, find confirmation count for specific transaction
            if (
                crypto_payment.status == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED
                and crypto_payment.tx_hashes
            ):
                try:
                    stored_txids = json.loads(crypto_payment.tx_hashes)
                    if stored_txids:
                        target_txid = stored_txids[
                            0
                        ]  # Duplicate payments store single txid
                        # Find the specific transaction
                        for tx in incoming:
                            tx_id = tx.get("txid") or tx.get("transaction_id")
                            if tx_id == target_txid:
                                old_confirmations = crypto_payment.current_confirmations
                                crypto_payment.current_confirmations = tx.get(
                                    "confirmations", 0
                                )
                                log.payment_debug(
                                    crypto_payment,
                                    f"Updated SPECIFIC transaction confirmations for duplicate payment: {old_confirmations} → {crypto_payment.current_confirmations} (TX: {target_txid[:16]}...)",
                                )
                                return
                        log.payment_error(
                            crypto_payment,
                            f"Could not find specific transaction {target_txid[:16]}... for duplicate payment",
                        )
                except json.JSONDecodeError:
                    log.payment_error(crypto_payment, "Invalid tx_hashes JSON")

            # Calculate total confirmations from incoming transfers (for non-duplicate payments)
            if incoming:
                min_confirmations = min(tx.get("confirmations", 0) for tx in incoming)
                old_confirmations = crypto_payment.current_confirmations
                crypto_payment.current_confirmations = min_confirmations
                log.payment_debug(
                    crypto_payment,
                    f"Updated INCOMING payment confirmations for refund-pending payment: {old_confirmations} → {min_confirmations} (refund confirmations: {crypto_payment.refund_confirmations})",
                )

        elif coin_type in ("DOGE", "BTC", "LTC", "BCH"):
            # Update confirmation count for DOGE/BTC/LTC/BCH using gettransaction
            try:
                stored_txids = json.loads(crypto_payment.tx_hashes or "[]")
                if not stored_txids:
                    log.payment_debug(crypto_payment, "No tx_hashes")
                    return

                # Get confirmation count for all transactions
                confirmations = []
                for txid in stored_txids:
                    try:
                        tx_detail = client.gettransaction(txid)
                        if tx_detail:
                            confirmations.append(tx_detail.get("confirmations", 0))
                    except Exception as e:
                        log.payment_error(
                            crypto_payment,
                            f"Failed to get confirmations for TX {txid[:16]}...: {e}",
                        )

                if confirmations:
                    min_confirmations = min(confirmations)
                    old_confirmations = crypto_payment.current_confirmations
                    crypto_payment.current_confirmations = min_confirmations
                    if min_confirmations != old_confirmations:
                        log.payment_info(
                            crypto_payment,
                            f"Updated {coin_type} confirmations: {old_confirmations} → {min_confirmations}",
                        )
                    else:
                        log.payment_debug(
                            crypto_payment,
                            f"No change in {coin_type} confirmations: {min_confirmations}",
                        )
            except json.JSONDecodeError:
                log.payment_error(crypto_payment, "Invalid tx_hashes JSON")

    except Exception as e:
        log.payment_error(
            crypto_payment,
            f"Failed to update confirmations for refund-pending payment: {e}",
        )


def process_sweep_confirmations(request, settings):
    """
    Monitor sweep transactions for confirmation status.
    Updates swept_confirmations and transitions status when fully confirmed.
    """
    log.processing_cycle("Starting sweep confirmation monitoring")
    db = request.dbsession

    # Query payments that need sweep confirmation monitoring
    sweep_queue = []

    # Query each coin type with its specific threshold
    for coin_type, required_confirmations in OUTBOUND_CONFIRMATIONS_REQUIRED.items():
        coin_sweeps = (
            db.query(CryptoPayment)
            .options(
                sa.orm.joinedload(CryptoPayment.user),
                sa.orm.joinedload(CryptoPayment.shop),
            )
            .filter(
                CryptoPayment.status == CryptoPayment.STATUS_CONFIRMED,
                CryptoPayment.coin_type == coin_type,
                CryptoPayment.swept_tx_hash != None,
                CryptoPayment.swept_confirmations < required_confirmations,
            )
            .all()
        )
        sweep_queue.extend(coin_sweeps)

    if not sweep_queue:
        log.processing_cycle("No sweep transactions need confirmation monitoring")
        return

    log.processing_cycle("Found sweep transactions to monitor", len(sweep_queue))

    # Group by coin type to get appropriate clients
    sweeps_by_coin = {}
    for payment in sweep_queue:
        coin_type = payment.coin_type
        if coin_type not in sweeps_by_coin:
            sweeps_by_coin[coin_type] = []
        sweeps_by_coin[coin_type].append(payment)

    # Process each coin type
    for coin_type, coin_sweeps in sweeps_by_coin.items():
        log.processing_cycle(
            f"Monitoring {coin_type} sweep transactions", len(coin_sweeps)
        )

        try:
            client = get_crypto_client(settings, coin_type)
        except ValueError as e:
            log.error_with_context(
                f"Failed to get {coin_type} client for sweep monitoring", e
            )
            continue

        for payment in coin_sweeps:
            try:
                # Get confirmation count for the sweep transaction
                confirmations = 0
                if coin_type == "XMR":
                    confirmations = get_monero_tx_confirmations(
                        client, payment.swept_tx_hash, payment.account_index
                    )
                elif coin_type == "DOGE":
                    confirmations = get_dogecoin_tx_confirmations(
                        client, payment.swept_tx_hash
                    )
                else:
                    log.payment_error(
                        payment,
                        f"Unsupported coin type for sweep monitoring: {coin_type}",
                    )
                    continue

                # Update confirmation count
                old_confirmations = payment.swept_confirmations
                payment.swept_confirmations = confirmations

                if confirmations != old_confirmations:
                    log.payment_info(
                        payment,
                        f"Sweep confirmations: {old_confirmations} → {confirmations}",
                    )

                # Check if sweep is now fully confirmed based on coin type requirements
                required_confirmations = OUTBOUND_CONFIRMATIONS_REQUIRED.get(
                    coin_type, 10
                )

                if confirmations >= required_confirmations:
                    old_status = payment.status
                    # Transition to confirmed-complete
                    payment.status = CryptoPayment.STATUS_CONFIRMED_COMPLETE
                    log.state_transition(
                        payment,
                        old_status,
                        payment.status,
                        f"sweep confirmed with {confirmations} confirmations",
                    )
                    log.payment_info(
                        payment,
                        f"Sweep fully confirmed - funds have left hot wallet",
                    )

                # Update timestamp
                payment.updated_timestamp = int(time.time() * 1000)
                db.add(payment)

            except Exception as e:
                log.payment_error(payment, "Failed to check sweep confirmations", e)
                continue

    log.processing_cycle("Finished sweep confirmation monitoring")


def scan_wallet_for_double_or_late_payments(request, settings):
    """
    Scan wallet for new incoming transactions since last scan position and match them to payments.
    This catches:
    1. Double/duplicate payments to already-paid addresses
    2. Late payments to expired/cancelled quotes that aren't actively monitored
    Uses scan position tracking to avoid rescanning old transfers.
    """
    log.processing_cycle("Starting wallet scan for double or late payments")
    db = request.dbsession

    # Get all active crypto processors (one per shop/coin combination)
    processors = db.query(CryptoProcessor).filter(CryptoProcessor.enabled == True).all()

    if not processors:
        log.processing_cycle("No active crypto processors found for scanning")
        return

    log.processing_cycle("Found processors to scan", len(processors))

    # Group processors by coin type for efficient scanning
    processors_by_coin = {}
    for processor in processors:
        coin_type = processor.coin_type
        if coin_type not in processors_by_coin:
            processors_by_coin[coin_type] = []
        processors_by_coin[coin_type].append(processor)

    # Process each coin type
    for coin_type, coin_processors in processors_by_coin.items():
        try:
            client = get_crypto_client(settings, coin_type)
        except ValueError as e:
            log.processing_cycle(f"Skipping {coin_type} wallet scan: {e}")
            continue

        log.processing_cycle(
            f"Scanning {coin_type} wallet for processors", len(coin_processors)
        )

        scan_start_time = time.time()

        if coin_type == "XMR":
            try:
                # Process each processor's account separately
                for processor in coin_processors:
                    # Get account index from wallet_label (for XMR it's the account index)
                    try:
                        account_index = int(processor.wallet_label)
                    except (ValueError, TypeError):
                        log.processing_cycle(
                            f"Processor {processor.id} has invalid wallet_label for XMR: {processor.wallet_label}"
                        )
                        continue

                    # Get this processor's scan position
                    scan_position = _get_scan_position_from_semaphore(
                        processor.last_scan_semaphore, coin_type
                    )
                    log.processing_cycle(
                        f"Processor {processor.id} (shop {processor.shop_id}, account {account_index}) scan position: {processor.last_scan_semaphore} → height {scan_position}"
                    )

                    # Build bounded query for this specific account
                    query_params = {
                        "in": True,
                        "out": False,
                        "pending": True,
                        "failed": False,
                        "pool": True,
                        "account_index": account_index,  # Scan only this account
                    }

                    # Add height bounds if we have a valid scan position
                    if scan_position > 0:
                        query_params["filter_by_height"] = True
                        query_params["min_height"] = scan_position
                        log.processing_cycle(
                            f"Scanning account {account_index} for transfers with min_height >= {scan_position}"
                        )
                    else:
                        log.processing_cycle(
                            f"Scanning ALL transfers for account {account_index} (no height filter)"
                        )

                    # Get transfers from the wallet using bounded query
                    log.processing_cycle(
                        f"Calling get_transfers with params: {query_params}"
                    )
                    result = client._call("get_transfers", query_params)

                    all_transfers = []
                    for transfer_type in ["in", "pending", "pool"]:
                        if transfer_type in result:
                            transfers_in_type = result[transfer_type]
                            all_transfers.extend(transfers_in_type)
                            log.processing_cycle(
                                f"Found transfers in '{transfer_type}' category",
                                len(transfers_in_type),
                            )

                    if not all_transfers:
                        log.processing_cycle(
                            f"No {coin_type} transfers found for account {account_index}"
                        )
                        continue

                    # Process all transfers returned by bounded query
                    # RPC already filtered by height, so all transfers are "new"
                    new_transfers = all_transfers
                    max_height = max(
                        (tx.get("height", 0) for tx in all_transfers), default=0
                    )

                    log.processing_cycle(
                        f"Found incoming {coin_type} transfers for account {account_index} newer than scan position {scan_position}, max height: {max_height}",
                        len(new_transfers),
                    )

                    # Log details of each transfer for debugging
                    for i, tx in enumerate(new_transfers):
                        subaddr = tx.get("subaddr_index", {})
                        log.processing_cycle(
                            f"Transfer {i+1}: height={tx.get('height', 'unknown')}, "
                            f"amount={tx.get('amount', 0) / 1e12:.12f} XMR, "
                            f"confirmations={tx.get('confirmations', 0)}, "
                            f"subaddr={subaddr.get('major', 0)}.{subaddr.get('minor', 'unknown')}, "
                            f"txid={tx.get('txid', 'unknown')[:16]}..."
                        )

                    # Process new transfers and match to payments
                    late_payments_found = 0
                    transfers_checked = 0
                    for tx in new_transfers:
                        transfers_checked += 1
                        subaddr = tx.get("subaddr_index", {})
                        if not subaddr:
                            log.processing_cycle(
                                f"Transfer {transfers_checked}: skipping - no subaddr_index"
                            )
                            continue

                        account_idx = subaddr.get("major", 0)
                        subaddr_idx = subaddr.get("minor")

                        if subaddr_idx is None:
                            log.processing_cycle(
                                f"Transfer {transfers_checked}: skipping - no minor subaddr"
                            )
                            continue

                        # Look up payment by subaddress
                        payment = (
                            db.query(CryptoPayment)
                            .options(
                                sa.orm.joinedload(CryptoPayment.user),
                                sa.orm.joinedload(CryptoPayment.shop),
                            )
                            .filter(
                                CryptoPayment.coin_type == coin_type,
                                CryptoPayment.account_index == account_idx,
                                CryptoPayment.subaddress_index == subaddr_idx,
                            )
                            .first()
                        )

                        if payment:
                            log.payment_info(
                                payment,
                                f"Transfer {transfers_checked} to subaddr {account_idx}.{subaddr_idx}: FOUND payment record (status {payment.status})",
                            )
                        else:
                            log.processing_cycle(
                                f"Transfer {transfers_checked} to subaddr {account_idx}.{subaddr_idx}: NO payment record"
                            )

                        if payment:
                            # First check if this transaction was already processed
                            txid = tx.get("txid") or tx.get("transaction_id")
                            try:
                                existing_txids = json.loads(payment.tx_hashes or "[]")
                            except (json.JSONDecodeError, TypeError):
                                existing_txids = []

                            if txid in existing_txids:
                                log.payment_debug(
                                    payment,
                                    f"Transaction {txid[:16]}... already processed, skipping",
                                )
                                continue

                            should_process = _should_process_late_payment(payment, tx)
                            log.payment_info(
                                payment,
                                f"should_process_late_payment: {should_process}",
                            )
                            if should_process:
                                late_payments_found += 1

                            # Check if this is a duplicate payment (original already has funds)
                            if payment.received_amount > 0:
                                log.payment_info(
                                    payment,
                                    f"DUPLICATE payment detected for {payment.status} quote: "
                                    f"{tx.get('amount', 0) / 1e12:.12f} XMR, "
                                    f"{tx.get('confirmations', 0)} confirmations, height {tx.get('height', 0)}",
                                )

                                # Check if duplicate payment record already exists for this transaction
                                existing_duplicate = (
                                    db.query(CryptoPayment)
                                    .filter(
                                        CryptoPayment.coin_type == coin_type,
                                        CryptoPayment.account_index == account_idx,
                                        CryptoPayment.subaddress_index == subaddr_idx,
                                        CryptoPayment.status
                                        == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                                        CryptoPayment.tx_hashes.contains(
                                            f'"{tx.get("txid")}"'
                                        ),
                                    )
                                    .first()
                                )

                                if existing_duplicate:
                                    log.payment_info(
                                        existing_duplicate,
                                        f"Duplicate payment record already exists for txid {tx.get('txid')}, processing refund",
                                    )
                                    duplicate_payment = existing_duplicate
                                else:
                                    # Create new payment object for each duplicate transaction
                                    duplicate_payment = _create_duplicate_payment(
                                        payment, tx, coin_type, db
                                    )
                                    db.add(duplicate_payment)
                                    db.flush()  # Get the ID assigned

                                    log.payment_info(
                                        duplicate_payment,
                                        "Created duplicate payment for refund processing",
                                    )

                                # Process the duplicate payment through refund pipeline
                                incoming = [tx]
                                process_payment(
                                    request, duplicate_payment, incoming, client=client
                                )
                            else:
                                # First payment to this address - process normally
                                # Determine if this is a late payment or double payment
                                if payment.status in [
                                    CryptoPayment.STATUS_EXPIRED,
                                    CryptoPayment.STATUS_CANCELLED,
                                ]:
                                    payment_type = "late payment"
                                else:
                                    payment_type = "double payment"

                                log.payment_info(
                                    payment,
                                    f"Found {payment_type} to {payment.status} quote: "
                                    f"{tx.get('amount', 0) / 1e12:.12f} XMR, "
                                    f"{tx.get('confirmations', 0)} confirmations, height {tx.get('height', 0)}",
                                )
                                incoming = [tx]
                                process_payment(
                                    request, payment, incoming, client=client
                                )

                    # Update scan position for THIS processor only
                    if max_height > 0 and max_height > scan_position:
                        new_semaphore = _format_scan_semaphore(coin_type, max_height)
                        processor.last_scan_semaphore = new_semaphore
                        db.add(processor)
                        log.processing_cycle(
                            f"Updated scan position for {processor.coin_type} processor {processor.id} (account {account_index}): "
                            f"{scan_position} → {max_height}"
                        )

                    log.processing_cycle(
                        f"Account {account_index} scan completed, found late payments",
                        late_payments_found,
                        f"scanned {len(new_transfers)} transfers",
                    )

                log.processing_cycle(
                    f"XMR wallet scan completed in ~{(time.time() - scan_start_time):.1f} seconds for all accounts"
                )

            except Exception as e:
                log.error_with_context(f"Failed to scan {coin_type} wallet", e)

        elif coin_type == "DOGE":
            try:
                # Get the minimum scan semaphore across all processors
                min_scan_semaphore = None
                for p in coin_processors:
                    if p.last_scan_semaphore and p.last_scan_semaphore.startswith(
                        "blockhash:"
                    ):
                        min_scan_semaphore = p.last_scan_semaphore.split(":", 1)[1]
                        break

                # Build bounded query for DOGE transfers using listsinceblock
                if min_scan_semaphore:
                    # Get transactions since the last block hash
                    result = client.listsinceblock(min_scan_semaphore)
                else:
                    # First scan - get recent transactions (last 100 blocks worth)
                    current_block_count = client.getblockcount()
                    recent_block_hash = client.getblockhash(
                        max(0, current_block_count - 100)
                    )
                    result = client.listsinceblock(recent_block_hash)

                all_transactions = result.get("transactions", [])
                latest_block_hash = result.get("lastblock")

                if not all_transactions:
                    log.processing_cycle(f"No {coin_type} transactions found")
                    # Still update semaphore even if no transactions
                    if latest_block_hash:
                        for processor in coin_processors:
                            processor.last_scan_semaphore = (
                                f"blockhash:{latest_block_hash}"
                            )
                            db.add(processor)
                    continue

                # Filter for incoming transactions only
                incoming_transactions = [
                    tx
                    for tx in all_transactions
                    if tx.get("category") == "receive"
                    and tx.get("confirmations", 0) >= 0
                ]

                log.processing_cycle(
                    f"Found incoming {coin_type} transactions newer than semaphore {min_scan_semaphore or 'genesis'}",
                    len(incoming_transactions),
                )

                # Process incoming transactions and match to payments
                late_payments_found = 0
                for tx in incoming_transactions:
                    txid = tx.get("txid")
                    if not txid:
                        continue

                    # Look up payment by address
                    payment = (
                        db.query(CryptoPayment)
                        .options(
                            sa.orm.joinedload(CryptoPayment.user),
                            sa.orm.joinedload(CryptoPayment.shop),
                        )
                        .filter(
                            CryptoPayment.coin_type == coin_type,
                            CryptoPayment.address == tx.get("address"),
                        )
                        .first()
                    )

                    if not payment:
                        continue

                    # Skip if this transaction was already processed for this payment
                    try:
                        existing_txids = json.loads(payment.tx_hashes or "[]")
                        if txid in existing_txids:
                            log.payment_debug(
                                payment,
                                f"Skipping already processed transaction {txid[:16]}...",
                            )
                            continue
                    except (json.JSONDecodeError, TypeError):
                        # If tx_hashes is malformed, treat as empty
                        existing_txids = []

                    # Check if this transaction already belongs to a different payment (prevent cross-payment matching)
                    existing_payment_with_tx = (
                        db.query(CryptoPayment)
                        .filter(
                            CryptoPayment.coin_type == coin_type,
                            CryptoPayment.tx_hashes.contains(f'"{txid}"'),
                            CryptoPayment.id != payment.id,
                        )
                        .first()
                    )

                    if existing_payment_with_tx:
                        log.payment_error(
                            payment,
                            f"Transaction {txid[:16]}... already belongs to payment {existing_payment_with_tx.id}, "
                            "not processing for this payment",
                        )
                        continue

                    if payment and _should_process_late_payment(payment, tx):
                        late_payments_found += 1
                        # Determine if this is a late payment or double payment
                        if payment.status in [
                            CryptoPayment.STATUS_EXPIRED,
                            CryptoPayment.STATUS_CANCELLED,
                        ]:
                            payment_type = "late payment"
                        else:
                            payment_type = "double payment"

                        log.payment_info(
                            payment,
                            f"Found {payment_type} to {payment.status} quote: "
                            f"{tx.get('amount', 0)} {coin_type}, "
                            f"{tx.get('confirmations', 0)} confirmations",
                        )

                        # Normalize amount to atomic units (koinu for DOGE)
                        coin_config = get_coin_config(coin_type)
                        atomic_units = int(coin_config["atomic_units"])
                        normalized_amount = int(
                            float(tx.get("amount", 0)) * atomic_units
                        )

                        # Create normalized transaction object for process_payment
                        normalized_tx = {
                            "txid": tx.get("txid", ""),
                            "amount": normalized_amount,  # koinu for DOGE
                            "confirmations": tx.get("confirmations", 0),
                            "address": tx.get("address"),
                        }

                        # Check if this is a duplicate payment (original already has funds)
                        if payment.received_amount > 0:
                            log.payment_info(
                                payment,
                                f"DUPLICATE payment detected for {payment.status} quote: "
                                f"{tx.get('amount', 0)} {coin_type} ({normalized_amount} koinu), "
                                f"{tx.get('confirmations', 0)} confirmations",
                            )

                            # Check if duplicate payment record already exists for this transaction
                            existing_duplicate = (
                                db.query(CryptoPayment)
                                .filter(
                                    CryptoPayment.coin_type == coin_type,
                                    CryptoPayment.address == tx.get("address"),
                                    CryptoPayment.status
                                    == CryptoPayment.STATUS_DOUBLEPAY_REFUNDED,
                                    CryptoPayment.tx_hashes.contains(
                                        f'"{tx.get("txid")}"'
                                    ),
                                )
                                .first()
                            )

                            if existing_duplicate:
                                log.payment_info(
                                    existing_duplicate,
                                    f"Duplicate payment record already exists for txid {tx.get('txid')}, processing refund",
                                )
                                duplicate_payment = existing_duplicate
                            else:
                                # Create new payment object for duplicate transaction
                                duplicate_payment = _create_duplicate_payment(
                                    payment, normalized_tx, coin_type, db
                                )
                                db.add(duplicate_payment)
                                db.flush()
                                log.payment_info(
                                    duplicate_payment,
                                    "Created duplicate payment for refund processing",
                                )

                            # Process the duplicate payment through refund pipeline
                            process_payment(
                                request,
                                duplicate_payment,
                                [normalized_tx],
                                client=client,
                            )
                        else:
                            # First payment to this address - process normally
                            log.payment_info(
                                payment,
                                f"Processing late payment to {payment.status} quote: "
                                f"{tx.get('amount', 0)} {coin_type} ({normalized_amount} koinu)",
                            )
                            process_payment(
                                request, payment, [normalized_tx], client=client
                            )

                # Update scan semaphore for all processors
                if latest_block_hash:
                    for processor in coin_processors:
                        processor.last_scan_semaphore = f"blockhash:{latest_block_hash}"
                        db.add(processor)
                        log.processing_cycle(
                            f"Updated scan semaphore for {processor.coin_type} processor {processor.id}: "
                            f"{min_scan_semaphore or 'genesis'} → {latest_block_hash[:16]}..."
                        )

                log.processing_cycle(
                    f"Wallet scan completed in ~{(time.time() - scan_start_time):.1f} seconds, found late payments",
                    late_payments_found,
                    f"scanned {len(incoming_transactions)} transactions",
                )

            except Exception as e:
                log.error_with_context(f"Failed to scan {coin_type} wallet", e)
                continue


def run_once(env, interval):
    request = env["request"]
    settings = request.registry.settings

    log.processing_cycle("Starting payment processing cycle")

    # First, do passive scan for late payments to expired/cancelled quotes
    with request.tm:
        try:
            scan_wallet_for_double_or_late_payments(request, settings)
        except Exception as e:
            log.error_with_context(
                "Failed to scan wallet for double or late payments", e
            )

    with request.tm:
        db = request.dbsession

        # Include both active payments and refund-pending payments that need confirmation monitoring
        all_monitored_statuses = (
            CryptoPayment.ACTIVE_STATUSES + CryptoPayment.REFUND_PENDING_STATUSES
        )

        q = (
            db.query(CryptoPayment)
            .options(
                sa.orm.joinedload(CryptoPayment.user),
                sa.orm.joinedload(CryptoPayment.shop),
            )
            .filter(
                CryptoPayment.status.in_(all_monitored_statuses),
                CryptoPayment.swept_tx_hash.is_(
                    None
                ),  # Only process payments that are not swept
            )
            .order_by(CryptoPayment.created_timestamp.asc())  # First come, first serve
        )
        payments = q.all()

        log.processing_cycle(
            f"Found payments to process",
            len(payments),
            f"{[(p.status, f'incoming:{p.current_confirmations}/{p.confirmations_required}', f'refund:{p.refund_confirmations}' if hasattr(p, 'refund_confirmations') and p.refund_confirmations > 0 else 'refund:N/A') for p in payments]}",
        )

        # Group payments by coin type to get appropriate clients
        payments_by_coin = {}
        for crypto_payment in payments:
            coin_type = crypto_payment.coin_type
            if coin_type not in payments_by_coin:
                payments_by_coin[coin_type] = []
            payments_by_coin[coin_type].append(crypto_payment)

        # Process each coin type separately
        for coin_type, coin_payments in payments_by_coin.items():
            log.processing_cycle(f"Processing {coin_type} payments", len(coin_payments))

            try:
                client = get_crypto_client(settings, coin_type)
            except ValueError as e:
                log.error_with_context(f"Failed to get client for {coin_type}", e)
                continue

            # CRITICAL: Sort payments by priority - using CryptoPayment.get_processing_priority()
            # Priority order: 0=refunds, 1=incoming, 2=other, 3=auto-sweep, 4=restocking fees

            sorted_payments = sorted(
                coin_payments, key=lambda p: p.get_processing_priority()
            )
            log.processing_cycle(
                f"Processing {coin_type} payments in priority order: duplicate refunds first"
            )

            for crypto_payment in sorted_payments:
                log.payment_info(
                    crypto_payment,
                    f"Processing payment (status: {crypto_payment.status}, coin: {crypto_payment.coin_type}, incoming: {crypto_payment.current_confirmations}/{crypto_payment.confirmations_required}, refund: {crypto_payment.refund_confirmations if crypto_payment.refund_confirmations else 'N/A'})",
                )

                # Skip if payment status changed (another process may have handled it)
                db.refresh(crypto_payment)
                log.payment_info(
                    crypto_payment,
                    f"[DEBUG] Checking status: {crypto_payment.status} in all_monitored_statuses: {crypto_payment.status in all_monitored_statuses}",
                )
                if crypto_payment.status not in all_monitored_statuses:
                    log.payment_info(
                        crypto_payment,
                        f"Skipping payment - status changed to {crypto_payment.status}",
                    )
                    continue

                    # Delete invoice for terminal state
                    delete_invoice_for_terminal_state(db, crypto_payment)
                    db.add(crypto_payment)
                    continue

                # For refund-pending payments, only update confirmations (don't do full processing)
                if crypto_payment.status in CryptoPayment.REFUND_PENDING_STATUSES:
                    log.payment_debug(
                        crypto_payment,
                        f"Updating INCOMING payment confirmations for refund-pending payment (status: {crypto_payment.status}, current: {crypto_payment.current_confirmations})",
                    )
                    update_payment_confirmations_only(client, crypto_payment, coin_type)
                    continue
                # Query transfers for the payment address
                if coin_type == "XMR":
                    # Monero: Query transfers for subaddress
                    res = (
                        client.get_transfers_for_subaddr(
                            crypto_payment.account_index,
                            [crypto_payment.subaddress_index],
                        )
                        or {}
                    )
                    incoming = res.get("in", []) or []

                    # Fallback: If no transfers found for subaddress, check all account transfers
                    # This helps with mempool transactions that might not immediately show up
                    # in subaddress-filtered queries
                    if not incoming:
                        log.payment_debug(
                            crypto_payment,
                            f"No transfers found for subaddress {crypto_payment.subaddress_index}, checking all account transfers",
                        )
                        try:
                            # Check all transfers for this account (including mempool)
                            all_transfers_result = client._call(
                                "get_transfers",
                                {
                                    "in": True,
                                    "out": False,
                                    "pending": True,
                                    "failed": False,
                                    "pool": True,  # Include mempool transactions
                                    "account_index": crypto_payment.account_index,
                                    # Don't filter by subaddr_indices - get all transfers
                                },
                            )

                            all_incoming = (
                                all_transfers_result.get("in", [])
                                if all_transfers_result
                                else []
                            )
                            # Also check pool (mempool) transactions
                            pool_incoming = (
                                all_transfers_result.get("pool", [])
                                if all_transfers_result
                                else []
                            )
                            all_incoming.extend(pool_incoming)

                            # Filter for our specific subaddress
                            for tx in all_incoming:
                                if (
                                    tx.get("subaddr_index", {}).get("minor")
                                    == crypto_payment.subaddress_index
                                    and tx.get("subaddr_index", {}).get("major")
                                    == crypto_payment.account_index
                                ):
                                    incoming.append(tx)
                                    log.payment_debug(
                                        crypto_payment,
                                        f"Found transfer for our subaddress in all-account query: {tx.get('txid', 'unknown')[:8]}...",
                                    )
                        except Exception as e:
                            log.payment_error(
                                crypto_payment,
                                f"Failed to query all account transfers for mempool fallback: {e}",
                            )

                    if incoming:
                        log.payment_debug(
                            crypto_payment, f"Found {len(incoming)} transfers"
                        )
                    else:
                        log.payment_debug(
                            crypto_payment,
                            f"No transfers found (subaddress {crypto_payment.subaddress_index})",
                        )
                elif coin_type == "DOGE":
                    # Dogecoin: Query received by address
                    incoming = get_dogecoin_incoming_transfers(client, crypto_payment)
                else:
                    log.payment_error(
                        crypto_payment,
                        f"Unsupported coin type for monitoring: {coin_type}",
                    )
                    incoming = []

                try:
                    # Process payment with a savepoint for rollback capability
                    savepoint = db.begin_nested()

                    process_payment(request, crypto_payment, incoming, client)

                    # Commit the savepoint if successful
                    savepoint.commit()

                except Exception as e:
                    # Rollback on any error
                    savepoint.rollback()
                    log.payment_error(
                        crypto_payment,
                        f"Failed to process payment: {e}",
                        exc_info=True,
                    )

        # Process refund confirmation monitoring
        process_refund_confirmations(request, settings)

        # Process sweep confirmation monitoring
        process_sweep_confirmations(request, settings)


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    log.processing_cycle(
        f"Crypto watcher started with interval {args.interval}s, once={args.once}"
    )

    try:
        while True:
            run_once(env, args.interval)
            if args.once:
                log.processing_cycle("Finished single run")
                break
            log.processing_cycle(f"Sleeping for {args.interval} seconds")
            time.sleep(args.interval)
    finally:
        log.processing_cycle("Shutting down")
        env["closer"]()


if __name__ == "__main__":
    main()
