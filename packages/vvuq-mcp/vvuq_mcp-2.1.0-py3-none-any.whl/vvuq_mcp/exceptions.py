"""
Custom exception classes for VVUQ-MCP domain errors.

These provide more specific error types than generic ValueError/Exception,
enabling better error handling and more informative error messages.
"""


class VVUQError(Exception):
    """Base exception for all VVUQ-MCP domain errors."""

    pass


class ContractNotFoundError(VVUQError):
    """Raised when a contract cannot be found by ID."""

    def __init__(self, contract_id: str):
        self.contract_id = contract_id
        super().__init__(f"Contract {contract_id} not found")


class ClaimNotFoundError(VVUQError):
    """Raised when a claim cannot be found in a contract."""

    def __init__(self, contract_id: str, claim_id: int):
        self.contract_id = contract_id
        self.claim_id = claim_id
        super().__init__(f"Claim {claim_id} not found in contract {contract_id}")


class AuthorizationError(VVUQError):
    """Raised when an agent attempts an unauthorized action."""

    pass


class InvalidContractStateError(VVUQError):
    """Raised when a contract is in an invalid state for the requested operation."""

    def __init__(self, contract_id: str, current_status: str, expected_status: str = "OPEN"):
        self.contract_id = contract_id
        self.current_status = current_status
        self.expected_status = expected_status
        super().__init__(
            f"Contract {contract_id} is not {expected_status} (current status: {current_status})"
        )


class ConfigurationError(VVUQError):
    """Raised when required configuration is missing or invalid."""

    pass


class ProofNotFoundError(VVUQError):
    """Raised when no accepted proof is found for a claim."""

    def __init__(self, claim_id: int, submitter_agent_id: str):
        self.claim_id = claim_id
        self.submitter_agent_id = submitter_agent_id
        super().__init__(
            f"No ACCEPTED proof found for claim {claim_id} by agent {submitter_agent_id}"
        )


class DuplicatePaymentError(VVUQError):
    """Raised when attempting to pay for a claim that was already paid."""

    def __init__(self, contract_id: str, claim_id: int):
        self.contract_id = contract_id
        self.claim_id = claim_id
        super().__init__(
            f"Duplicate payment attempt: Claim {claim_id} in contract {contract_id} "
            "has already been paid. This is a race condition or double-spending attempt."
        )


class SecurityViolationError(VVUQError):
    """Raised when a security violation is detected."""

    pass


class InvalidDependencyError(VVUQError):
    """Raised when a Lean4 dependency is invalid."""

    pass


class VerificationFailedError(VVUQError):
    """Raised when proof verification fails."""

    pass
