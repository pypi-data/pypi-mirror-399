"""
Cryptographic utilities for VVUQ-MCP payment receipts.

Uses HMAC-SHA256 for signing payment receipts and SHA256 for proof hashing.
"""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime
from typing import Literal

from vvuq_mcp.models import PaymentReceipt

# Initialize logger
logger = logging.getLogger(__name__)


def sign_payment(
    payment_id: str,
    amount: float,
    from_agent: str,
    to_agent: str,
    contract_id: str,
    claim_id: int,
    timestamp: str,
    secret_key: str,
) -> str:
    """
    Sign a payment receipt using HMAC-SHA256.

    Args:
        payment_id: Unique payment identifier
        amount: Payment amount
        from_agent: Agent making the payment
        to_agent: Agent receiving the payment
        contract_id: Associated contract ID
        claim_id: Associated claim ID
        timestamp: ISO format timestamp
        secret_key: Secret key for signing (must be at least 32 bytes/64 hex chars)

    Returns:
        64-character hex HMAC-SHA256 signature

    Raises:
        ValueError: If secret key is too weak (< 32 bytes)
    """
    # Security: Validate secret key strength (minimum 256 bits = 32 bytes)
    if len(secret_key) < 64:  # 32 bytes = 64 hex chars
        raise ValueError(
            "SECURITY: Secret key too weak! Must be at least 32 bytes (64 hex characters). "
            "Use secrets.token_hex(32) to generate a strong key."
        )

    # Create canonical message for signing
    message = f"{payment_id}|{amount}|{from_agent}|{to_agent}|{contract_id}|{claim_id}|{timestamp}"

    # Compute HMAC-SHA256
    signature = hmac.new(
        key=secret_key.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return signature


def verify_payment(
    payment_id: str,
    amount: float,
    from_agent: str,
    to_agent: str,
    contract_id: str,
    claim_id: int,
    timestamp: str,
    signature: str,
    secret_key: str,
) -> bool:
    """
    Verify a payment receipt signature.

    Args:
        payment_id: Unique payment identifier
        amount: Payment amount
        from_agent: Agent making the payment
        to_agent: Agent receiving the payment
        contract_id: Associated contract ID
        claim_id: Associated claim ID
        timestamp: ISO format timestamp
        signature: HMAC-SHA256 signature to verify
        secret_key: Secret key used for signing

    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = sign_payment(
        payment_id=payment_id,
        amount=amount,
        from_agent=from_agent,
        to_agent=to_agent,
        contract_id=contract_id,
        claim_id=claim_id,
        timestamp=timestamp,
        secret_key=secret_key,
    )

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)


def generate_payment_id() -> str:
    """
    Generate a unique payment ID.

    Returns:
        Unique payment ID with "pay-" prefix
    """
    return f"pay-{uuid.uuid4().hex}"


def hash_proof(proof_code: str) -> str:
    """
    Hash proof code using SHA256 for integrity verification.

    Args:
        proof_code: Lean4 proof code

    Returns:
        64-character hex SHA256 hash
    """
    return hashlib.sha256(proof_code.encode("utf-8")).hexdigest()


def create_payment_receipt(
    amount: float,
    from_agent: str,
    to_agent: str,
    contract_id: str,
    claim_id: int,
    transaction_type: Literal["credit", "debit"],
    secret_key: str,
) -> PaymentReceipt:
    """
    Create a complete signed payment receipt.

    Args:
        amount: Payment amount
        from_agent: Agent making the payment
        to_agent: Agent receiving the payment
        contract_id: Associated contract ID
        claim_id: Associated claim ID
        transaction_type: "credit" or "debit"
        secret_key: Secret key for signing

    Returns:
        PaymentReceipt with valid signature
    """
    payment_id = generate_payment_id()
    timestamp = datetime.now()

    signature = sign_payment(
        payment_id=payment_id,
        amount=amount,
        from_agent=from_agent,
        to_agent=to_agent,
        contract_id=contract_id,
        claim_id=claim_id,
        timestamp=timestamp.isoformat(),
        secret_key=secret_key,
    )

    return PaymentReceipt(
        payment_id=payment_id,
        amount=amount,
        from_agent=from_agent,
        to_agent=to_agent,
        contract_id=contract_id,
        claim_id=claim_id,
        signature=signature,
        timestamp=timestamp,
        transaction_type=transaction_type,
    )
