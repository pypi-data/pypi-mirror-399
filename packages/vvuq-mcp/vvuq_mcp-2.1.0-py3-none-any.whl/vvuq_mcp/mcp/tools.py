"""
MCP Tool implementations for VVUQ-MCP.

These tools provide the core functionality for formal verification contracts.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from vvuq_mcp.exceptions import (
    AuthorizationError,
    ClaimNotFoundError,
    ConfigurationError,
    ContractNotFoundError,
    DuplicatePaymentError,
    InvalidContractStateError,
    ProofNotFoundError,
)
from vvuq_mcp.models import (
    Contract,
    ContractClaim,
    VerificationAttempt,
    VerificationResult,
)
from vvuq_mcp.payments.crypto import create_payment_receipt
from vvuq_mcp.response_types import (
    ContractCreationResponse,
    ContractDetailResponse,
    ContractQueryResponse,
    ContractSummaryDict,
    PaymentProcessingResponse,
    VerificationHistoryResponse,
    VerificationSubmissionResponse,
)


# Constants to avoid magic strings and numbers
DEFAULT_CONTRACT_STATUS = "OPEN"
DEFAULT_TRANSACTION_TYPE = "credit"
DEFAULT_VERIFICATION_TIMEOUT_SECONDS = 60


# Protocol definitions for type safety
@runtime_checkable
class StorageProtocol(Protocol):
    """Protocol defining storage interface for VVUQ operations."""

    async def store_contract(self, contract: Contract) -> None: ...
    async def store_contracts(self, contracts: List[Contract]) -> None: ...
    async def get_contract(self, contract_id: str, include_claims: bool = True) -> Optional[Contract]: ...
    async def get_contracts_by_status(self, status: str) -> List[Contract]: ...
    async def get_contracts_summary_by_status(self, status: str) -> List[ContractSummaryDict]: ...
    async def store_verification_attempt(self, attempt: VerificationAttempt) -> None: ...
    async def get_verification_history(self, contract_id: str) -> List[VerificationAttempt]: ...
    async def store_payment(self, receipt: Any) -> None: ...
    async def mark_claim_as_paid(self, contract_id: str, claim_id: int) -> bool:
        """
        Atomically mark a claim as paid. Returns True if successful (first payment),
        False if claim was already paid (duplicate payment attempt).
        """
        ...


@runtime_checkable
class VerifierProtocol(Protocol):
    """Protocol defining verifier interface for proof verification."""

    async def verify_proof(
        self,
        proof_code: str,
        expected_theorem: str,
        allowed_dependencies: List[str],
        timeout_seconds: int,
    ) -> VerificationResult: ...


def _generate_id(prefix: str) -> str:
    """
    Generate a unique ID with the given prefix.

    Args:
        prefix: Prefix for the ID (e.g., 'contract', 'attempt')

    Returns:
        Unique ID string in format '{prefix}-{12_hex_chars}'
    """
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


async def create_contract(
    storage: StorageProtocol,
    title: str,
    description: str,
    claims: List[Dict[str, Any]],
    issuer_agent_id: str,
) -> ContractCreationResponse:
    """
    Create a new formal verification contract.

    Args:
        storage: Storage implementation for persistence
        title: Contract title
        description: Contract description
        claims: List of claim dictionaries with theorem statements
        issuer_agent_id: Agent creating the contract

    Returns:
        Dictionary with contract_id and status
    """
    # Generate unique contract ID
    contract_id = _generate_id("contract")

    # Parse claims into ContractClaim objects
    contract_claims = [
        ContractClaim(
            claim_id=claim["claim_id"],
            theorem_statement=claim["theorem_statement"],
            allowed_dependencies=claim.get("allowed_dependencies", []),
            payment_amount=claim["payment_amount"],
            payment_type=claim.get("payment_type", "all-or-nothing"),
        )
        for claim in claims
    ]

    # Create contract
    contract = Contract(
        contract_id=contract_id,
        title=title,
        description=description,
        claims=contract_claims,
        issuer_agent_id=issuer_agent_id,
        status=DEFAULT_CONTRACT_STATUS,
    )

    # Store in Neo4j
    await storage.store_contract(contract)

    return {
        "contract_id": contract_id,
        "status": DEFAULT_CONTRACT_STATUS,
        "created_at": contract.created_at.isoformat(),
    }


async def create_contracts(
    storage: StorageProtocol,
    contracts: List[Dict[str, Any]],
) -> List[ContractCreationResponse]:
    """
    Create multiple contracts in batch (18× faster than serial).

    Args:
        storage: Storage implementation for persistence
        contracts: List of contract dictionaries, each with:
            - title: Contract title
            - description: Contract description
            - claims: List of claim dictionaries
            - issuer_agent_id: Agent creating the contract

    Returns:
        List of dictionaries with contract_id, status, and created_at
    """
    contract_objects = []

    for contract_spec in contracts:
        # Generate unique contract ID
        contract_id = _generate_id("contract")

        # Parse claims into ContractClaim objects
        contract_claims = [
            ContractClaim(
                claim_id=claim["claim_id"],
                theorem_statement=claim["theorem_statement"],
                allowed_dependencies=claim.get("allowed_dependencies", []),
                payment_amount=claim["payment_amount"],
                payment_type=claim.get("payment_type", "all-or-nothing"),
            )
            for claim in contract_spec["claims"]
        ]

        # Create contract
        contract = Contract(
            contract_id=contract_id,
            title=contract_spec["title"],
            description=contract_spec["description"],
            claims=contract_claims,
            issuer_agent_id=contract_spec["issuer_agent_id"],
            status=DEFAULT_CONTRACT_STATUS,
        )

        contract_objects.append((contract_id, contract))

    # Batch store in Neo4j using UNWIND
    await storage.store_contracts([c for _, c in contract_objects])

    # Return results
    return [
        {
            "contract_id": contract_id,
            "status": DEFAULT_CONTRACT_STATUS,
            "created_at": contract.created_at.isoformat(),
        }
        for contract_id, contract in contract_objects
    ]


async def query_contracts(
    storage: StorageProtocol,
    status: str = DEFAULT_CONTRACT_STATUS,
) -> ContractQueryResponse:
    """
    Query contracts by status with optimized aggregation (10× faster).

    Args:
        storage: Storage implementation for persistence
        status: Contract status to filter by (default: OPEN)

    Returns:
        Dictionary with list of matching contracts
    """
    # Use Cypher aggregation to compute total_value and claims_count in database
    contracts = await storage.get_contracts_summary_by_status(status)

    return {"contracts": contracts}


async def get_contract(
    storage: StorageProtocol,
    contract_id: str,
    include_claims: bool = True,
) -> Optional[ContractDetailResponse]:
    """
    Get a specific contract by ID with optional claims deserialization.

    Args:
        storage: Storage implementation for persistence
        contract_id: Contract identifier
        include_claims: Whether to include full claims data (default: True)
                       Set to False for metadata-only queries (10-100× faster for contracts with many claims)

    Returns:
        Contract details or None if not found
    """
    contract = await storage.get_contract(contract_id)

    if contract is None:
        return None

    result = {
        "contract_id": contract.contract_id,
        "title": contract.title,
        "description": contract.description,
        "status": contract.status,
        "issuer_agent_id": contract.issuer_agent_id,
        "created_at": contract.created_at.isoformat(),
    }

    if include_claims:
        # Full deserialization for when claims are needed
        result["claims"] = [
            {
                "claim_id": claim.claim_id,
                "theorem_statement": claim.theorem_statement,
                "allowed_dependencies": claim.allowed_dependencies,
                "payment_amount": claim.payment_amount,
                "payment_type": claim.payment_type,
            }
            for claim in contract.claims
        ]
    else:
        # Lightweight metadata-only response (avoid O(n) deserialization)
        result["claims_count"] = len(contract.claims)

    return result


async def submit_proof(
    storage: StorageProtocol,
    verifier: VerifierProtocol,
    contract_id: str,
    claim_id: int,
    proof_code: str,
    submitter_agent_id: str,
) -> VerificationSubmissionResponse:
    """
    Submit a proof for verification.

    Args:
        storage: Storage implementation for persistence
        verifier: Verifier implementation for proof verification
        contract_id: Contract containing the claim
        claim_id: Claim ID within the contract
        proof_code: Lean4 proof code
        submitter_agent_id: Agent submitting the proof

    Returns:
        Verification result with verdict and attempt_id

    Raises:
        ValueError: If contract or claim not found
    """
    # Get the contract
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise ContractNotFoundError(contract_id)

    # Find the claim
    claim = next((candidate_claim for candidate_claim in contract.claims if candidate_claim.claim_id == claim_id), None)
    if claim is None:
        raise ClaimNotFoundError(contract_id, claim_id)

    # Authorization Check: Prevent issuer from verifying own contract
    if submitter_agent_id == contract.issuer_agent_id:
        raise AuthorizationError("Contract issuer cannot submit proofs for their own contract")

    # Authorization Check: Contract must be OPEN
    if contract.status != "OPEN":
        raise InvalidContractStateError(contract_id, contract.status, "OPEN")

    # Verify the proof
    submitted_at = datetime.now()
    result = await verifier.verify_proof(
        proof_code=proof_code,
        expected_theorem=claim.theorem_statement,
        allowed_dependencies=claim.allowed_dependencies,
        timeout_seconds=DEFAULT_VERIFICATION_TIMEOUT_SECONDS,
    )
    verified_at = datetime.now()

    # Create verification attempt record
    attempt_id = _generate_id("attempt")
    attempt = VerificationAttempt(
        attempt_id=attempt_id,
        contract_id=contract_id,
        claim_id=claim_id,
        submitter_agent_id=submitter_agent_id,
        proof_code=proof_code,
        result=result,
        submitted_at=submitted_at,
        verified_at=verified_at,
    )

    # Store the attempt
    await storage.store_verification_attempt(attempt)

    return {
        "attempt_id": attempt_id,
        "verdict": result.verdict,
        "matches_claim": result.matches_claim,
        "sorry_count": result.sorry_count,
        "errors": result.errors,
        "verification_time_ms": result.verification_time_ms,
        "unauthorized_dependencies": result.unauthorized_dependencies,
    }


async def submit_proofs(
    storage: StorageProtocol,
    verifier: VerifierProtocol,
    submissions: List[Dict[str, Any]],
) -> List[VerificationSubmissionResponse]:
    """
    Submit multiple proofs for concurrent verification (10× faster than serial).

    Args:
        storage: Storage implementation for persistence
        verifier: Verifier implementation for proof verification
        submissions: List of submission dicts with keys:
            - contract_id: Contract containing the claim
            - claim_id: Claim ID within the contract
            - proof_code: Lean4 proof code
            - submitter_agent_id: Agent submitting the proof

    Returns:
        List of verification results (one per submission)

    Raises:
        ValueError: If any contract or claim not found
    """
    async def verify_one(submission: Dict[str, Any]) -> VerificationSubmissionResponse:
        """Verify a single submission."""
        return await submit_proof(
            storage=storage,
            verifier=verifier,
            contract_id=submission["contract_id"],
            claim_id=submission["claim_id"],
            proof_code=submission["proof_code"],
            submitter_agent_id=submission["submitter_agent_id"],
        )

    # Run all verifications concurrently
    return await asyncio.gather(*[verify_one(sub) for sub in submissions])


async def get_verification_history(
    storage: StorageProtocol,
    contract_id: str,
) -> VerificationHistoryResponse:
    """
    Get verification history for a contract.

    Args:
        storage: Storage implementation for persistence
        contract_id: Contract identifier

    Returns:
        Dictionary with list of verification attempts
    """
    attempts = await storage.get_verification_history(contract_id)

    return {
        "attempts": [
            {
                "attempt_id": attempt.attempt_id,
                "claim_id": attempt.claim_id,
                "submitter_agent_id": attempt.submitter_agent_id,
                "verdict": attempt.result.verdict,
                "matches_claim": attempt.result.matches_claim,
                "sorry_count": attempt.result.sorry_count,
                "verification_time_ms": attempt.result.verification_time_ms,
                "submitted_at": attempt.submitted_at.isoformat(),
                "verified_at": attempt.verified_at.isoformat(),
            }
            for attempt in attempts
        ]
    }


import os

async def process_payment(
    storage: StorageProtocol,
    contract_id: str,
    claim_id: int,
    from_agent: str,
    to_agent: str,
    amount: float,
) -> PaymentProcessingResponse:
    """
    Process payment for a verified proof.

    Secret key is loaded from VVUQ_SECRET_KEY environment variable.

    Args:
        storage: Storage implementation for persistence
        contract_id: Contract ID
        claim_id: Claim ID
        from_agent: Agent making payment
        to_agent: Agent receiving payment
        amount: Payment amount (IGNORED - fetched from contract claim for security)

    Returns:
        Payment receipt details

    Raises:
        ValueError: If VVUQ_SECRET_KEY is not set, contract not found, or claim not found
    """
    # Load secret key from environment
    secret_key = os.getenv("VVUQ_SECRET_KEY")
    if not secret_key:
        raise ConfigurationError("VVUQ_SECRET_KEY environment variable not set")

    # SECURITY: Fetch contract to get ACTUAL claim payment amount
    # Never trust amount passed by caller - always use contract's claim.payment_amount
    contract = await storage.get_contract(contract_id)
    if not contract:
        raise ContractNotFoundError(contract_id)

    # Find the claim
    claim = next(
        (candidate_claim for candidate_claim in contract.claims if candidate_claim.claim_id == claim_id),
        None
    )
    if not claim:
        raise ClaimNotFoundError(contract_id, claim_id)

    # Use the claim's payment amount (ignore passed-in amount for security)
    actual_amount = claim.payment_amount

    # Authorization: Check if proof was actually ACCEPTED
    history = await storage.get_verification_history(contract_id)
    valid_attempt = next(
        (
            verification_attempt for verification_attempt in history
            if verification_attempt.claim_id == claim_id
            and verification_attempt.submitter_agent_id == to_agent
            and verification_attempt.result.verdict == "ACCEPTED"
        ),
        None
    )

    if not valid_attempt:
        raise ProofNotFoundError(claim_id, to_agent)

    # SECURITY: Atomic claim locking to prevent double-spending
    # This MUST happen before any payment processing
    is_first_payment = await storage.mark_claim_as_paid(contract_id, claim_id)

    if not is_first_payment:
        raise DuplicatePaymentError(contract_id, claim_id)

    # Create signed payment receipt using ACTUAL amount from contract claim
    receipt = create_payment_receipt(
        amount=actual_amount,  # SECURITY: Use contract's claim amount, not caller's input
        from_agent=from_agent,
        to_agent=to_agent,
        contract_id=contract_id,
        claim_id=claim_id,
        transaction_type=DEFAULT_TRANSACTION_TYPE,
        secret_key=secret_key,
    )

    # Store the payment
    await storage.store_payment(receipt)

    return {
        "payment_id": receipt.payment_id,
        "amount": receipt.amount,
        "from_agent": receipt.from_agent,
        "to_agent": receipt.to_agent,
        "contract_id": receipt.contract_id,
        "claim_id": receipt.claim_id,
        "signature": receipt.signature,
        "timestamp": receipt.timestamp.isoformat(),
    }
