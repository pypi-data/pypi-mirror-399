import uuid
from decimal import Decimal

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Numeric,
    UnicodeText,
    Unicode,
    Boolean,
)
from sqlalchemy.orm import relationship

from .meta import Base, RBase, UUIDType, foreign_key, now_timestamp


class CryptoPayment(RBase, Base):
    """
    Represents a cryptocurrency payment intent tied to a single Invoice.
    Amounts are stored in the smallest unit (e.g., satoshis for BTC, piconero for XMR).
    """

    # Payment status constants
    STATUS_PENDING = "pending"
    STATUS_RECEIVED = "received"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CONFIRMED_COMPLETE = (
        "confirmed-complete"  # Confirmed and swept to cold storage
    )
    STATUS_CONFIRMED_OVERPAY = "confirmed-overpay"
    STATUS_CONFIRMED_OVERPAY_REFUNDED = "confirmed-overpay-refunded"
    STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE = "confirmed-overpay-refunded-complete"
    STATUS_EXPIRED = "expired"
    STATUS_LATEPAY_REFUNDED = "latepay-refunded"
    STATUS_LATEPAY_REFUNDED_COMPLETE = "latepay-refunded-complete"
    STATUS_UNDERPAID_REFUNDED = "underpaid-refunded"
    STATUS_UNDERPAID_REFUNDED_COMPLETE = "underpaid-refunded-complete"
    STATUS_CANCELLED = "cancelled"
    STATUS_OUT_OF_STOCK_REFUNDED = "out-of-stock-refunded"
    STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE = "out-of-stock-refunded-complete"
    STATUS_DOUBLEPAY_REFUNDED = "doublepay-refunded"
    STATUS_DOUBLEPAY_REFUNDED_COMPLETE = "doublepay-refund-complete"

    # Not-refunded states (when no refund wallet configured)
    STATUS_LATEPAY_NOT_REFUNDED = "latepay-not-refunded"
    STATUS_UNDERPAID_NOT_REFUNDED = "underpaid-not-refunded"
    STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED = "confirmed-overpay-not-refunded"
    STATUS_OUT_OF_STOCK_NOT_REFUNDED = "out-of-stock-not-refunded"
    STATUS_DOUBLEPAY_NOT_REFUNDED = "doublepay-not-refunded"

    # === SEMANTIC STATE GROUPS ===
    # These groups define business logic categories for easier maintenance

    # Initial/waiting states - payments that are starting or waiting for processing
    # These states don't transition from 'received' - they are entry points
    INITIAL_WAITING_STATUSES = [
        STATUS_PENDING,  # Initial state for new payments
        STATUS_LATEPAY_REFUNDED,  # Initial state for late payment objects (refund in progress)
        STATUS_DOUBLEPAY_REFUNDED,  # Initial state for duplicate payment objects (refund in progress)
    ]

    # Successful payment statuses - customer received product, keep invoice
    SUCCESSFUL_PAYMENT_STATUSES = [
        STATUS_CONFIRMED,  # Normal successful payment
        STATUS_CONFIRMED_COMPLETE,  # Confirmed and swept to cold storage
        STATUS_CONFIRMED_OVERPAY,  # Overpaid but confirmed, refund pending
        STATUS_CONFIRMED_OVERPAY_REFUNDED,  # Overpaid, refund in progress
        STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE,  # Overpaid, refund complete
    ]

    # Failed payment statuses - customer did not receive product, delete invoice
    FAILED_PAYMENT_STATUSES = [
        STATUS_EXPIRED,  # Payment window expired
        STATUS_CANCELLED,  # User cancelled payment
        STATUS_LATEPAY_REFUNDED_COMPLETE,  # Late payment, refund complete
        STATUS_LATEPAY_NOT_REFUNDED,  # Late payment, no refund wallet
        STATUS_UNDERPAID_REFUNDED,  # Insufficient payment, refund in progress
        STATUS_UNDERPAID_REFUNDED_COMPLETE,  # Insufficient payment, refund complete
        STATUS_UNDERPAID_NOT_REFUNDED,  # Insufficient payment, no refund wallet
        STATUS_OUT_OF_STOCK_REFUNDED,  # Product unavailable, refund in progress
        STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE,  # Product unavailable, refund complete
        STATUS_OUT_OF_STOCK_NOT_REFUNDED,  # Product unavailable, no refund wallet
        STATUS_DOUBLEPAY_REFUNDED_COMPLETE,  # Duplicate payment, refund complete
        STATUS_DOUBLEPAY_NOT_REFUNDED,  # Duplicate payment, no refund wallet
        STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED,  # Overpaid but no refund wallet configured
    ]

    # === OPERATIONAL STATE GROUPS ===
    # These groups define processing behavior for the crypto watcher

    # Active statuses that should be processed by the watcher
    ACTIVE_STATUSES = [
        STATUS_PENDING,
        STATUS_RECEIVED,
        STATUS_CONFIRMED,  # Still active until swept
        STATUS_CONFIRMED_OVERPAY,
        STATUS_DOUBLEPAY_REFUNDED,  # Double payment that needs refund processing
    ]

    # Statuses that need confirmation monitoring but may have refunds pending
    REFUND_PENDING_STATUSES = [
        STATUS_LATEPAY_REFUNDED,  # Refund sent, but may need more incoming confirmations
        STATUS_UNDERPAID_REFUNDED,  # Refund sent, but may need more incoming confirmations
        STATUS_CONFIRMED_OVERPAY_REFUNDED,  # Overpayment refund sent, needs confirmation monitoring
        STATUS_OUT_OF_STOCK_REFUNDED,  # Refund sent, but may need more incoming confirmations
        # STATUS_DOUBLEPAY_REFUNDED moved to ACTIVE_STATUSES - needs refund initiation, not monitoring
    ]

    # Terminal statuses that should not be processed (have no outgoing transitions)
    TERMINAL_STATUSES = [
        # Successful terminal states
        STATUS_CONFIRMED_COMPLETE,  # Normal successful payment that has been swept
        STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE,  # Overpaid, refund complete
        # Failed terminal states
        STATUS_EXPIRED,  # Payment window expired
        STATUS_CANCELLED,  # User cancelled payment
        STATUS_LATEPAY_REFUNDED_COMPLETE,  # Late payment, refund complete
        STATUS_LATEPAY_NOT_REFUNDED,  # Late payment, no refund wallet
        STATUS_UNDERPAID_REFUNDED_COMPLETE,  # Insufficient payment, refund complete
        STATUS_UNDERPAID_NOT_REFUNDED,  # Insufficient payment, no refund wallet
        STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE,  # Product unavailable, refund complete
        STATUS_OUT_OF_STOCK_NOT_REFUNDED,  # Product unavailable, no refund wallet
        STATUS_DOUBLEPAY_REFUNDED_COMPLETE,  # Duplicate payment, refund complete
        STATUS_DOUBLEPAY_NOT_REFUNDED,  # Duplicate payment, no refund wallet
        STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED,  # Overpaid but no refund wallet configured
    ]

    # Statuses that trigger redirect to crypto quotes history (refund/no-refund scenarios)
    REFUND_REDIRECT_STATUSES = [
        # All failed payment statuses redirect to history
        STATUS_EXPIRED,
        STATUS_CANCELLED,
        STATUS_LATEPAY_REFUNDED,
        STATUS_LATEPAY_REFUNDED_COMPLETE,
        STATUS_LATEPAY_NOT_REFUNDED,
        STATUS_UNDERPAID_REFUNDED,
        STATUS_UNDERPAID_REFUNDED_COMPLETE,
        STATUS_UNDERPAID_NOT_REFUNDED,
        STATUS_OUT_OF_STOCK_REFUNDED,
        STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE,
        STATUS_OUT_OF_STOCK_NOT_REFUNDED,
        STATUS_DOUBLEPAY_REFUNDED,
        STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
        STATUS_DOUBLEPAY_NOT_REFUNDED,
        STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED,
        # Overpay refund in progress also redirects
        STATUS_CONFIRMED_OVERPAY_REFUNDED,
    ]

    id = Column(UUIDType, primary_key=True, index=True)
    invoice_id = Column(UUIDType, foreign_key("Invoice", "id"), nullable=True)
    # Always store user and shop - we know these when creating crypto payment
    user_id = Column(UUIDType, foreign_key("User", "id"), nullable=False)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    # optional: the shop location used for fulfillment (for physical products)
    shop_location_id = Column(
        UUIDType, foreign_key("ShopLocation", "id"), nullable=True
    )

    address = Column(String(128), nullable=False)
    account_index = Column(Integer, nullable=False, default=0)
    subaddress_index = Column(Integer, nullable=False)

    # Coin type (e.g., 'XMR', 'BTC', 'LTC', 'DOGE')
    coin_type = Column(String(10), nullable=False)

    # expected and observed amounts in atomic units (satoshis, piconero, etc.)
    expected_amount = Column(BigInteger, nullable=False)
    received_amount = Column(BigInteger, nullable=False, default=0)
    received_network_fee = Column(
        BigInteger, nullable=True
    )  # Customer's tx fee (when available from RPC)

    # Fee amount calculated at payment creation (to avoid expensive RPC calls on page loads)
    estimated_fee_amount = Column(
        BigInteger, nullable=True
    )  # Estimated fee in atomic units (piconero, satoshis, etc.)

    # locked rate at the time of creating the payment (USD per coin)
    rate_locked_usd_per_coin = Column(Numeric(18, 8), nullable=False)

    quote_expires_at = Column(BigInteger, nullable=False)
    confirmations_required = Column(Integer, nullable=False, default=10)

    status = Column(String(64), nullable=False, default="pending")
    # store as JSON string for DB portability
    tx_hashes = Column(UnicodeText, nullable=False)

    # Shop's wallet configuration at time of payment (for recovery/sweeping)
    shop_sweep_to_address = Column(
        Unicode(256), nullable=True
    )  # Where to sweep funds for this payment

    # Customer's refund address (optional, provided at checkout)
    refund_address = Column(
        Unicode(256), nullable=True
    )  # Where to send refunds if payment fails/expires

    # Refund reason for audit trail
    refund_reason = Column(
        UnicodeText, nullable=True
    )  # Why the refund was issued (out of stock, expired, etc.)

    # Refund tracking
    refund_tx_hash = Column(
        Unicode(128), nullable=True
    )  # Transaction hash of the refund
    refund_amount = Column(BigInteger, nullable=True)  # Amount refunded in atomic units
    refund_confirmations = Column(
        Integer, nullable=False, default=0
    )  # Current confirmation count of refund transaction

    # Sweep tracking
    swept_amount = Column(BigInteger, nullable=True)  # Amount swept in atomic units
    swept_tx_hash = Column(Unicode(128), nullable=True)  # Transaction hash of the sweep
    swept_timestamp = Column(BigInteger, nullable=True)  # When the sweep occurred
    swept_network_fee = Column(
        BigInteger, nullable=True
    )  # Network fee paid (in atomic units, from node)
    swept_confirmations = Column(
        Integer, nullable=False, default=0
    )  # Current confirmation count of sweep transaction

    # Current confirmation count
    current_confirmations = Column(
        Integer, nullable=False, default=0
    )  # Current number of confirmations

    # Email tracking to prevent duplicates
    sales_email_sent = Column(
        Boolean, nullable=False, default=False
    )  # Boolean: whether sale confirmation email has been sent
    purchase_email_sent = Column(
        Boolean, nullable=False, default=False
    )  # Boolean: whether purchase confirmation email has been sent
    refund_email_sent = Column(
        Boolean, nullable=False, default=False
    )  # Boolean: whether refund notification email has been sent

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    invoice = relationship("Invoice", backref="crypto_payment")
    user = relationship("User")
    shop = relationship("Shop")
    shop_location = relationship("ShopLocation", uselist=False)

    def __init__(
        self,
        invoice,
        user,
        shop,
        address,
        account_index,
        subaddress_index,
        coin_type,
        expected_amount,
        rate_locked_usd_per_coin: Decimal,
        quote_expires_at_ms: int,
        confirmations_required: int = 10,
        shop_location=None,
        shop_sweep_to_address=None,
        refund_address=None,
        estimated_fee_amount=None,
    ):
        self.id = uuid.uuid1()
        self.invoice = invoice
        self.user = user
        self.shop = shop
        self.address = address
        self.account_index = account_index
        self.subaddress_index = subaddress_index
        self.coin_type = coin_type
        self.expected_amount = int(expected_amount)
        self.received_amount = 0
        self.estimated_fee_amount = estimated_fee_amount
        self.rate_locked_usd_per_coin = rate_locked_usd_per_coin
        self.quote_expires_at = int(quote_expires_at_ms)
        self.confirmations_required = confirmations_required
        self.status = self.STATUS_PENDING
        self.tx_hashes = "[]"
        self.shop_location = shop_location
        self.shop_sweep_to_address = shop_sweep_to_address
        self.refund_address = refund_address
        now = now_timestamp()
        self.created_timestamp = now
        self.updated_timestamp = now

    @property
    def is_expired(self) -> bool:
        return now_timestamp() > self.quote_expires_at and self.received_amount == 0

    @property
    def due_amount(self) -> int:
        return max(0, self.expected_amount - self.received_amount)

    @property
    def is_swept(self) -> bool:
        """Check if this payment has been swept to cold storage."""
        return self.swept_tx_hash is not None

    @property
    def available_to_sweep(self) -> int:
        """Calculate amount available to sweep for this specific payment."""
        if self.is_swept or self.received_amount == 0:
            return 0
        # Return the received amount for this specific payment
        return self.received_amount

    @property
    def confirmation_status(self) -> str:
        """Get confirmation status as a user-friendly string (e.g., '2/10')."""
        return f"{self.current_confirmations}/{self.confirmations_required}"

    @property
    def is_fully_confirmed(self) -> bool:
        """Check if payment has reached required confirmation count."""
        return self.current_confirmations >= self.confirmations_required

    def is_finalized(self) -> bool:
        """Check if payment has been finalized (customer received their product).

        Only payments in confirmed statuses with sufficient funds and confirmations
        can be considered truly finalized.
        """
        # Must be in a status that could potentially be finalized
        if self.status not in [
            self.STATUS_CONFIRMED,
            self.STATUS_CONFIRMED_OVERPAY,
            self.STATUS_CONFIRMED_OVERPAY_REFUNDED,
        ]:
            return False

        # Must have received sufficient funds (at least expected amount)
        if not (self.received_amount >= self.expected_amount):
            return False

        # Must have sufficient confirmations
        if not (self.current_confirmations >= self.confirmations_required):
            return False

        return True

    def get_processing_priority(self) -> int:
        """
        Get payment processing priority for crypto watcher operations.

        Priority order ensures proper fund flow:
        0=refunds (customer service), 1=incoming, 2=other (pending, terminals),
        3=auto-sweep (shop owner), 4=restocking fees (most dangerous - dead last).

        CRITICAL: Terminal states with restocking fees (confirmed refunds) are Priority 4
        and blocked by mid-tier confirmation requirements to prevent premature sweeps.
        Restocking fee sweeps are most dangerous and happen after everything else.

        Returns:
            int: Priority level (0=highest, 4=lowest)
        """
        match self.status:
            # Priority 0: Refunds - highest priority (customer service)
            case (
                self.STATUS_DOUBLEPAY_REFUNDED
                | self.STATUS_LATEPAY_REFUNDED
                | self.STATUS_UNDERPAID_REFUNDED
                | self.STATUS_OUT_OF_STOCK_REFUNDED
            ):
                return 0  # Process refunds first

            # Priority 1: Incoming payments (new money)
            case self.STATUS_RECEIVED:
                return 1  # Process new payments

            # Priority 3: Auto-sweep operations to shop owner
            case self.STATUS_CONFIRMED | self.STATUS_CONFIRMED_OVERPAY:
                return 3  # Auto-sweep to shop owner

            # Priority 4: Restocking fee sweeps - most dangerous, dead last
            case (
                self.STATUS_LATEPAY_REFUNDED_COMPLETE
                | self.STATUS_UNDERPAID_REFUNDED_COMPLETE
                | self.STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE
                | self.STATUS_DOUBLEPAY_REFUNDED_COMPLETE
            ):
                return 4  # Restocking fee sweeps - most dangerous

            # Priority 2: All other statuses (pending, monitoring, intermediate states)
            case _:
                return 2  # Everything else in middle

    # State transition validation
    VALID_TRANSITIONS = {
        STATUS_PENDING: [STATUS_RECEIVED, STATUS_EXPIRED, STATUS_CANCELLED],
        STATUS_RECEIVED: [
            STATUS_CONFIRMED,
            STATUS_CONFIRMED_OVERPAY,
            STATUS_UNDERPAID_REFUNDED,  # Underpayment detected
            STATUS_DOUBLEPAY_REFUNDED,  # Duplicate detected
            STATUS_OUT_OF_STOCK_REFUNDED,  # Out of stock
        ],
        STATUS_CONFIRMED: [
            STATUS_CONFIRMED_COMPLETE
        ],  # Can transition to complete after sweep
        STATUS_CONFIRMED_COMPLETE: [],  # Terminal - confirmed and swept
        STATUS_CONFIRMED_OVERPAY: [
            STATUS_CONFIRMED_OVERPAY_REFUNDED,
        ],
        STATUS_CONFIRMED_OVERPAY_REFUNDED: [
            STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE,
            STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED,  # No refund wallet configured
        ],
        STATUS_CONFIRMED_OVERPAY_REFUNDED_COMPLETE: [],  # Terminal
        STATUS_EXPIRED: [],  # Terminal - late payments create new payment objects
        STATUS_LATEPAY_REFUNDED: [
            STATUS_LATEPAY_REFUNDED_COMPLETE,
            STATUS_LATEPAY_NOT_REFUNDED,  # No refund wallet configured
        ],
        STATUS_LATEPAY_REFUNDED_COMPLETE: [],  # Terminal
        STATUS_UNDERPAID_REFUNDED: [
            STATUS_UNDERPAID_REFUNDED_COMPLETE,
            STATUS_UNDERPAID_NOT_REFUNDED,  # No refund wallet configured
        ],
        STATUS_UNDERPAID_REFUNDED_COMPLETE: [],  # Terminal
        STATUS_CANCELLED: [],  # Terminal
        STATUS_OUT_OF_STOCK_REFUNDED: [
            STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE,
            STATUS_OUT_OF_STOCK_NOT_REFUNDED,  # No refund wallet configured
        ],
        STATUS_OUT_OF_STOCK_REFUNDED_COMPLETE: [],  # Terminal
        STATUS_DOUBLEPAY_REFUNDED: [
            STATUS_DOUBLEPAY_REFUNDED_COMPLETE,
            STATUS_DOUBLEPAY_NOT_REFUNDED,  # No refund wallet configured
        ],
        STATUS_DOUBLEPAY_REFUNDED_COMPLETE: [],  # Terminal
        # Not-refunded states (terminal)
        STATUS_LATEPAY_NOT_REFUNDED: [],  # Terminal
        STATUS_UNDERPAID_NOT_REFUNDED: [],  # Terminal
        STATUS_CONFIRMED_OVERPAY_NOT_REFUNDED: [],  # Terminal
        STATUS_OUT_OF_STOCK_NOT_REFUNDED: [],  # Terminal
        STATUS_DOUBLEPAY_NOT_REFUNDED: [],  # Terminal
    }

    def is_valid_transition(self, new_status: str) -> bool:
        """
        Check if transitioning from current status to new_status is allowed.

        Args:
            new_status: The status to transition to

        Returns:
            bool: True if transition is valid, False otherwise
        """
        if self.status not in self.VALID_TRANSITIONS:
            # Unknown current status - allow transition (for backwards compatibility)
            return True

        allowed_transitions = self.VALID_TRANSITIONS[self.status]
        return new_status in allowed_transitions

    def validate_and_set_status(self, new_status: str, context: str = "") -> bool:
        """
        Validate and set a new status with logging.

        Args:
            new_status: The status to transition to
            context: Optional context for logging (e.g., "overpayment refund")

        Returns:
            bool: True if transition was successful, False if invalid
        """
        import logging

        logger = logging.getLogger(__name__)

        if not self.is_valid_transition(new_status):
            logger.error(
                f"Invalid state transition for payment {self.id}: "
                f"{self.status} → {new_status} "
                f"(context: {context}). Valid transitions: {self.VALID_TRANSITIONS.get(self.status, [])}"
            )
            return False

        old_status = self.status
        self.status = new_status

        logger.info(
            f"Payment {self.id} state transition: {old_status} → {new_status}"
            + (f" (context: {context})" if context else "")
        )

        return True

    def get_valid_next_statuses(self) -> list:
        """
        Get list of valid statuses this payment can transition to.

        Returns:
            list: List of valid next status strings
        """
        return self.VALID_TRANSITIONS.get(self.status, [])

    def is_successful_payment(self) -> bool:
        """
        Check if this payment represents a successful transaction.

        Returns:
            bool: True if customer received product, False otherwise
        """
        return self.status in self.SUCCESSFUL_PAYMENT_STATUSES

    def is_failed_payment(self) -> bool:
        """
        Check if this payment represents a failed transaction.

        Returns:
            bool: True if customer did not receive product, False otherwise
        """
        return self.status in self.FAILED_PAYMENT_STATUSES

    def should_keep_invoice(self) -> bool:
        """
        Check if this payment's invoice should be preserved.

        Business Logic: Keep invoices for successful payments.

        Returns:
            bool: True if invoice should be kept, False if it should be deleted
        """
        return self.is_successful_payment()

    def is_initial_waiting_state(self) -> bool:
        """
        Check if this payment is in an initial or waiting state.

        These states represent entry points that don't transition from 'received':
        - pending: Initial state for new payments
        - latepay_refunded: Initial state for late payment objects
        - doublepay_refund: Initial state for duplicate payment objects

        Returns:
            bool: True if payment is in initial/waiting state, False otherwise
        """
        return self.status in self.INITIAL_WAITING_STATUSES

    def _format_amount(self, amount: int) -> str:
        """Convert atomic units to display format for the coin type."""
        if self.coin_type == "XMR":
            return f"{amount / 1e12:.12f}".rstrip("0").rstrip(".")
        else:  # BTC, LTC, BCH, DOGE all use 8 decimals
            return f"{amount / 1e8:.8f}".rstrip("0").rstrip(".")

    def __str__(self) -> str:
        """
        Human-readable string representation for logging and debugging.

        Returns:
            str: Concise payment description for logs
        """
        # Get amount information
        expected_display = self._format_amount(self.expected_amount)
        received_display = self._format_amount(self.received_amount)

        # Build status description
        status_desc = self.status

        # Format confirmations
        conf_desc = f"{self.current_confirmations or 0}/{self.confirmations_required}"

        # Get user display name if available
        user_display = ""
        if self.user and hasattr(self.user, "name") and self.user.name:
            user_display = f" user:{self.user.name}"

        # Get shop name if available
        shop_display = ""
        if self.shop and hasattr(self.shop, "name") and self.shop.name:
            shop_display = f" shop:{self.shop.name}"

        return (
            f"Payment {self.uuid_str[:8]} [{status_desc}] "
            f"{self.coin_type} {received_display}/{expected_display} "
            f"conf:{conf_desc} addr:{self.address[-8:]}{user_display}{shop_display}"
        )

    def __repr__(self) -> str:
        """
        Developer-oriented string representation for debugging.

        Returns:
            str: Detailed payment description for debugging
        """
        return (
            f"CryptoPayment(id={self.uuid_str[:8]}, "
            f"status={self.status}, "
            f"coin={self.coin_type}, "
            f"expected={self.expected_amount}, "
            f"received={self.received_amount}, "
            f"confirmations={self.current_confirmations or 0}/{self.confirmations_required}, "
            f"invoice_id={self.invoice_id.hex[:8] if self.invoice_id else None})"
        )

    def format_amount_details(self) -> str:
        """
        Format detailed amount information for logging.

        Returns:
            str: Detailed amount breakdown
        """
        expected = self._format_amount(self.expected_amount)
        received = self._format_amount(self.received_amount)
        due = self._format_amount(self.due_amount) if self.due_amount > 0 else "0"

        return f"expected:{expected} received:{received} due:{due} {self.coin_type}"

    def format_confirmation_status(self) -> str:
        """
        Format confirmation status for logging.

        Returns:
            str: Confirmation status description
        """
        current = self.current_confirmations or 0
        return f"{current}/{self.confirmations_required}"
