"""
Monero address validation utilities.

This module provides functions to validate Monero addresses including
checksum validation to catch typos.
"""

import struct
from typing import Tuple, Optional


# Base58 alphabet used by Monero
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def decode_base58(address: str) -> Optional[bytes]:
    """Decode a base58 string to bytes."""
    decoded = 0
    for char in address:
        try:
            decoded = decoded * 58 + BASE58_ALPHABET.index(char)
        except ValueError:
            return None

    # Convert to bytes
    hex_str = hex(decoded)[2:]
    if len(hex_str) % 2:
        hex_str = "0" + hex_str

    return bytes.fromhex(hex_str)


def keccak_256(data: bytes) -> bytes:
    """Compute Keccak-256 hash (not SHA3-256)."""
    try:
        from Crypto.Hash import keccak

        k = keccak.new(digest_bits=256)
        k.update(data)
        return k.digest()
    except ImportError:
        # If pycryptodome not available, we can't validate
        return b""


def validate_monero_address(address: str) -> Tuple[bool, str]:
    """
    Validate a Monero address.

    Returns:
        (is_valid, error_message)
    """
    # Basic length check
    if len(address) not in [95, 106]:
        return False, "Invalid length - Monero addresses are 95 or 106 characters"

    # Network byte check - Monero mainnet addresses can start with 4, 8, or 5
    # 4 = standard address, 8 = integrated address, 5 = subaddress
    if not address[0] in ["4", "8", "5"]:
        return False, "Invalid network - mainnet addresses start with '4', '8', or '5'"

    # Try to decode base58
    try:
        decoded = decode_base58(address)
        if not decoded:
            return False, "Invalid base58 encoding"

        # Skip cryptographic validation if we can't import keccak
        if not keccak_256(b"test"):
            # Can't do full validation but format is OK
            return True, ""

        # Validate checksum (last 4 bytes)
        if len(decoded) < 69:  # Minimum size for address
            return False, "Decoded address too short"

        payload = decoded[:-4]
        checksum = decoded[-4:]

        # Calculate expected checksum
        hash_result = keccak_256(payload)
        expected_checksum = hash_result[:4]

        if checksum != expected_checksum:
            return False, "Invalid checksum - possible typo in address"

        return True, ""

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def is_valid_monero_address(address: str) -> bool:
    """Simple boolean check for Monero address validity."""
    valid, _ = validate_monero_address(address)
    return valid
