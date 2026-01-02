"""
Payment rescue module for handling crypto payment errors with automatic refunds.

Handles:
- Underpayments: Refund partial payments minus 9% restocking fee
- Overpayments: Refund excess amount minus 9% restocking fee 
- Expired quotes: Refund late payments minus 9% restocking fee
"""

import logging
from decimal import Decimal
from ...models.user_crypto_refund_address import get_user_crypto_refund_address

logger = logging.getLogger(__name__)

RESTOCKING_FEE_PERCENT = Decimal("0.09")  # 9% restocking fee
OVERPAYMENT_THRESHOLD_PERCENT = Decimal("0.05")  # 5% overpayment allowed before refund

# Dogecoin fee buffer - increase if you see "INSUFFICIENT FUNDS" errors in logs
# This accounts for network fees that Dogecoin adds on top of outputs
# Actual fees are typically 0.001-0.003 DOGE for 2-output transactions
DOGE_REFUND_FEE_BUFFER = 0.005  # Conservative buffer to avoid insufficient funds

# Minimum economically viable refund amount in USD
# Below this threshold, network fees likely exceed the refund value
import os

MINIMUM_VIABLE_REFUND_USD = Decimal(
    os.environ.get("MINIMUM_VIABLE_REFUND_USD", "0.069")  # Default: 6.9 cents USD
)


def calculate_refund_amount(amount, fee_percent=RESTOCKING_FEE_PERCENT):
    """Calculate refund amount after deducting restocking fee."""
    fee = amount * fee_percent
    refund = amount - fee
    # Ensure refund is not negative
    return max(refund, Decimal("0"))


def is_refund_economically_viable(refund_amount, coin_type, usd_per_coin=None):
    """
    Check if a refund is economically viable based on USD value.

    Args:
        refund_amount: The refund amount in coin units (not atomic)
        coin_type: The cryptocurrency type (e.g., 'DOGE', 'XMR')
        usd_per_coin: The USD exchange rate per coin (from payment.rate_locked_usd_per_coin)

    Returns:
        bool: True if refund is economically viable, False otherwise
    """
    if usd_per_coin is None:
        # If no USD rate provided, always allow refund (backwards compatibility)
        return True

    # Convert refund amount to USD
    refund_usd = refund_amount * Decimal(str(usd_per_coin))

    # Check if refund USD value meets minimum threshold
    return refund_usd >= MINIMUM_VIABLE_REFUND_USD


class PaymentRescue:
    """Handle crypto payment errors and trigger refunds when appropriate."""

    def __init__(self, dbsession, crypto_client):
        self.dbsession = dbsession
        self.crypto_client = crypto_client

    def get_user_refund_address(self, user, shop, crypto_type):
        """Get user's configured refund address for the crypto type."""
        if not user or not shop:
            return None

        refund_record = get_user_crypto_refund_address(
            self.dbsession, user, shop, crypto_type
        )
        return refund_record.address if refund_record else None

    def handle_underpayment(self, payment, expected_amount, received_amount, user):
        """
        Handle underpayment scenario.

        Args:
            payment: CryptoPayment object
            expected_amount: Expected amount in crypto units
            received_amount: Actually received amount in crypto units
            user: User object who made the payment

        Returns:
            dict with refund details or None if no refund possible
        """
        shop = payment.shop or (payment.invoice.shop if payment.invoice else None)
        refund_address = self.get_user_refund_address(user, shop, payment.coin_type)
        if not refund_address:
            return None

        # Calculate refund amount (received minus fee)
        refund_amount = calculate_refund_amount(received_amount)

        if refund_amount <= 0:
            return None

        # Check if refund is economically viable
        economically_viable = is_refund_economically_viable(
            refund_amount, payment.coin_type, payment.rate_locked_usd_per_coin
        )

        if not economically_viable:
            refund_usd = refund_amount * Decimal(str(payment.rate_locked_usd_per_coin))
            logger.warning(
                f"Economically unviable refund for {payment}: "
                f"refund amount {refund_amount} {payment.coin_type} "
                f"(${refund_usd:.4f} USD) below ${MINIMUM_VIABLE_REFUND_USD} threshold"
            )

        return {
            "type": "underpayment",
            "payment_id": payment.id,
            "refund_address": refund_address,
            "received_amount": received_amount,
            "expected_amount": expected_amount,
            "refund_amount": refund_amount,
            "fee_amount": received_amount - refund_amount,
            "reason": f"Underpayment: received {received_amount} but expected {expected_amount}",
            "economically_viable": economically_viable,
        }

    def handle_overpayment(self, payment, expected_amount, received_amount, user):
        """
        Handle overpayment scenario.

        Args:
            payment: CryptoPayment object
            expected_amount: Expected amount in crypto units
            received_amount: Actually received amount in crypto units
            user: User object who made the payment

        Returns:
            dict with refund details or None if no refund possible
        """
        # Check if overpayment exceeds threshold
        overpayment_ratio = (received_amount - expected_amount) / expected_amount
        if overpayment_ratio <= OVERPAYMENT_THRESHOLD_PERCENT:
            # Within acceptable threshold, no refund needed
            return None

        shop = payment.shop or (payment.invoice.shop if payment.invoice else None)
        refund_address = self.get_user_refund_address(user, shop, payment.coin_type)
        if not refund_address:
            return None

        # Calculate excess amount
        excess_amount = received_amount - expected_amount

        # Calculate refund on the excess (minus fee)
        refund_amount = calculate_refund_amount(excess_amount)

        if refund_amount <= 0:
            return None

        return {
            "type": "overpayment",
            "payment_id": payment.id,
            "refund_address": refund_address,
            "received_amount": received_amount,
            "expected_amount": expected_amount,
            "excess_amount": excess_amount,
            "refund_amount": refund_amount,
            "fee_amount": excess_amount - refund_amount,
            "payment_amount": expected_amount,  # Shop should get the actual payment too!
            "reason": f"Overpayment exceeds {int(OVERPAYMENT_THRESHOLD_PERCENT * 100)}% threshold: received {received_amount} but expected {expected_amount}",
        }

    def handle_expired_payment(self, payment, received_amount, user):
        """
        Handle payment received after quote expiration.

        Args:
            payment: CryptoPayment object
            received_amount: Actually received amount in crypto units
            user: User object who made the payment

        Returns:
            dict with refund details or None if no refund possible
        """
        shop = payment.shop or (payment.invoice.shop if payment.invoice else None)
        refund_address = self.get_user_refund_address(user, shop, payment.coin_type)
        if not refund_address:
            return None

        # Calculate refund amount (received minus fee)
        refund_amount = calculate_refund_amount(received_amount)

        if refund_amount <= 0:
            return None

        # Check if refund is economically viable
        economically_viable = is_refund_economically_viable(
            refund_amount, payment.coin_type, payment.rate_locked_usd_per_coin
        )

        if not economically_viable:
            refund_usd = refund_amount * Decimal(str(payment.rate_locked_usd_per_coin))
            logger.warning(
                f"Economically unviable refund for expired {payment}: "
                f"refund amount {refund_amount} {payment.coin_type} "
                f"(${refund_usd:.4f} USD) below ${MINIMUM_VIABLE_REFUND_USD} threshold"
            )

        return {
            "type": "expired",
            "payment_id": payment.id,
            "refund_address": refund_address,
            "received_amount": received_amount,
            "refund_amount": refund_amount,
            "fee_amount": received_amount - refund_amount,
            "reason": "Payment received after quote expiration",
            "economically_viable": economically_viable,
        }

    def execute_refund(self, refund_details, payment=None):
        """
        Execute the actual refund transaction.

        Now implements multi-output transactions:
        - Customer gets refund minus fee
        - Shop owner gets the fee portion

        Args:
            refund_details: dict with refund information
            payment: CryptoPayment object (needed for account_index and shop_sweep_to_address)

        Returns:
            dict with transaction details or raises exception
        """
        import logging

        logger = logging.getLogger(__name__)

        refund_amount_coin = refund_details["refund_amount"]
        fee_amount_coin = refund_details["fee_amount"]
        # For overpayments, also include the actual payment amount
        payment_amount_coin = refund_details.get("payment_amount", Decimal("0"))

        # Get coin type and atomic units for proper logging
        coin_type = payment.coin_type if payment else "XMR"
        from . import get_coin_config

        coin_config = get_coin_config(coin_type)
        atomic_units = int(coin_config["atomic_units"])
        refund_amount_atomic = int(refund_amount_coin * atomic_units)
        fee_amount_atomic = int(fee_amount_coin * atomic_units)
        payment_amount_atomic = int(payment_amount_coin * atomic_units)

        atomic_unit_name = (
            "piconero"
            if coin_type == "XMR"
            else "koinu" if coin_type == "DOGE" else "atomic units"
        )

        # Get shop sweep address - we'll handle missing address with a clear error
        shop_sweep_address = payment.shop_sweep_to_address if payment else None

        if payment:
            logger.info(f"Attempting to refund: {payment}")
            if payment_amount_coin > 0:
                logger.info(
                    f"Multi-output refund - Customer: {refund_amount_coin} {coin_type}, "
                    f"Shop: {payment_amount_coin + fee_amount_coin} {coin_type} (payment + fee)"
                )
            else:
                logger.info(
                    f"Refund: {refund_amount_coin} {coin_type} to customer, "
                    f"{fee_amount_coin} {coin_type} fee to shop"
                )

        # Check if incoming payment has enough confirmations before allowing refund
        from . import get_coin_config

        coin_config = get_coin_config(payment.coin_type if payment else "XMR")
        required_confirmations = coin_config.get("confirmations_required", 10)

        if payment and payment.current_confirmations < required_confirmations:
            logger.info(f"Refund delayed - insufficient confirmations: {payment}")
            return {
                "success": False,
                "error": f"Incoming payment needs {required_confirmations - payment.current_confirmations} more confirmations before refund",
                "refund_details": refund_details,
                "confirmations_needed": required_confirmations
                - payment.current_confirmations,
            }

        # Get wallet balance for fee calculations
        balance_result = None
        if coin_type == "DOGE":
            try:
                balance_result = self.crypto_client.getbalance()
            except Exception:
                pass

        try:
            # Create coin-specific refund transaction
            if coin_type == "XMR":
                # Monero always uses multi-output transfer
                if not shop_sweep_address:
                    raise ValueError("Shop sweep address is required for refunds")

                account_index = payment.account_index if payment else 0

                # Build destinations array
                destinations = [
                    {
                        "address": refund_details["refund_address"],
                        "amount": refund_amount_atomic,
                    }
                ]

                # For overpayments, combine payment amount and fee into single shop output
                shop_amount_atomic = fee_amount_atomic
                if payment_amount_atomic > 0:
                    shop_amount_atomic += payment_amount_atomic

                destinations.append(
                    {
                        "address": shop_sweep_address,
                        "amount": shop_amount_atomic,
                    }
                )

                transfer_params = {
                    "destinations": destinations,
                    "account_index": account_index,
                    "get_tx_key": True,
                    "do_not_relay": False,
                    "priority": 1,
                }
                tx_result = self.crypto_client._call("transfer", transfer_params)

            elif coin_type == "DOGE":
                # Dogecoin always uses sendmany for multi-output
                if not shop_sweep_address:
                    raise ValueError("Shop sweep address is required for refunds")

                # Round to 8 decimal places to match DOGE precision requirements
                refund_amount_doge = round(float(refund_amount_coin), 8)
                fee_amount_doge = round(float(fee_amount_coin), 8)
                payment_amount_doge = (
                    round(float(payment_amount_coin), 8)
                    if payment_amount_coin > 0
                    else 0
                )

                # Initial outputs - will be adjusted below if needed
                outputs = {}

                # For overpayments, combine payment amount and fee into single shop output
                shop_amount_doge = fee_amount_doge
                if payment_amount_doge > 0:
                    shop_amount_doge = round(payment_amount_doge + fee_amount_doge, 8)

                # Account for network fee by reducing amounts proportionally
                # Dogecoin sendmany adds fee on top of outputs, so we need to leave room
                total_output = refund_amount_doge + shop_amount_doge

                # Fee estimate - can be overridden via environment variable
                import os

                estimated_fee = float(
                    os.environ.get(
                        "DOGE_REFUND_FEE_BUFFER", str(DOGE_REFUND_FEE_BUFFER)
                    )
                )
                if estimated_fee != DOGE_REFUND_FEE_BUFFER:
                    logger.info(
                        f"Using custom fee buffer from env: {estimated_fee} DOGE"
                    )

                # Check if we need to adjust for fees
                if balance_result and total_output + estimated_fee > balance_result:
                    # Calculate how much we need to reduce
                    shortage = (total_output + estimated_fee) - balance_result

                    # Reduce both amounts proportionally
                    refund_ratio = refund_amount_doge / total_output
                    shop_ratio = shop_amount_doge / total_output

                    # Round down to 3 decimal places
                    import math

                    refund_amount_doge = (
                        math.floor(
                            (refund_amount_doge - shortage * refund_ratio) * 1000
                        )
                        / 1000
                    )
                    shop_amount_doge = (
                        math.floor((shop_amount_doge - shortage * shop_ratio) * 1000)
                        / 1000
                    )

                # Build final outputs with adjusted amounts
                outputs[refund_details["refund_address"]] = refund_amount_doge
                outputs[shop_sweep_address] = shop_amount_doge

                # Get the account for the payment address
                from_account = ""
                try:
                    from_account = self.crypto_client._call(
                        "getaccount", [payment.address]
                    )
                except Exception:
                    pass

                # Clean outputs - ensure plain floats
                clean_outputs = {
                    addr: float(amount) for addr, amount in outputs.items()
                }

                # Try sendmany with the account that has the funds
                try:
                    tx_hash = self.crypto_client.sendmany(
                        from_account, clean_outputs, 1
                    )
                except Exception as e:
                    error_msg = str(e).lower()
                    if "insufficient funds" in error_msg:
                        # Log detailed fee information when we hit insufficient funds
                        logger.error(f"INSUFFICIENT FUNDS - Fee estimate too low!")
                        logger.error(f"Current fee buffer: {estimated_fee} DOGE")
                        logger.error(
                            f"Total outputs: {sum(clean_outputs.values())} DOGE"
                        )
                        logger.error(f"Available balance: {balance_result} DOGE")
                        shortfall = (
                            sum(clean_outputs.values()) + estimated_fee - balance_result
                        )
                        logger.error(
                            f"Shortfall: {shortfall:.8f} DOGE (may need more for actual network fee)"
                        )
                        logger.error(
                            f"ACTION REQUIRED: Increase DOGE_REFUND_FEE_BUFFER constant at top of crypto_payment_rescue.py"
                        )

                        # Try with default account as fallback
                        try:
                            tx_hash = self.crypto_client.sendmany("", clean_outputs, 1)
                        except Exception as e2:
                            if "insufficient funds" in str(e2).lower():
                                logger.error(
                                    f"Both accounts failed - fee definitely too low!"
                                )
                            raise e2
                    else:
                        raise

                tx_result = {"tx_hash": tx_hash}

                # Log success with fee info for monitoring
                logger.info(f"Refund sent successfully! TX: {tx_hash}")
                if balance_result:
                    buffer_used = balance_result - sum(clean_outputs.values())
                    logger.info(
                        f"Fee buffer used: {buffer_used:.8f} DOGE (estimated: {estimated_fee})"
                    )

            else:
                raise ValueError(f"Refund not supported for coin type: {coin_type}")

            if payment:
                logger.info(f"Refund transaction successful: {payment} - {tx_result}")
            else:
                logger.info(
                    f"Refund transaction successful for payment {refund_details['payment_id']}: {tx_result}"
                )

            return {
                "success": True,
                "tx_hash": tx_result.get("tx_hash"),
                "refund_details": refund_details,
                "fee_charged": refund_details["fee_amount"],
            }

        except Exception as e:
            if payment:
                logger.error(f"Refund failed: {payment} - {e}")
            else:
                logger.error(
                    f"Refund failed for payment {refund_details['payment_id']}: {e}"
                )
            return {"success": False, "error": str(e), "refund_details": refund_details}
