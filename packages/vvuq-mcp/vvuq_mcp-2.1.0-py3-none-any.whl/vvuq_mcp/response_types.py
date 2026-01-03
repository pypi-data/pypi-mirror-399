"""
Response type definitions for VVUQ-MCP tools.

These TypedDict classes define the structure of responses from tool functions,
providing type safety without the overhead of Pydantic models.
"""

from typing import Any, Dict, List, TypedDict


class ContractCreationResponse(TypedDict):
    """Response for contract creation."""

    contract_id: str
    status: str
    created_at: str


class ContractDetailResponse(TypedDict, total=False):
    """Response for contract details (some fields optional)."""

    contract_id: str
    title: str
    description: str
    status: str
    issuer_agent_id: str
    created_at: str
    claims: List[Dict[str, Any]]  # Will be fixed separately
    claims_count: int


class ContractSummaryDict(TypedDict):
    """Summary information for a contract."""

    contract_id: str
    title: str
    status: str
    claims_count: int
    total_value: float
    issuer_agent_id: str
    created_at: str


class ContractQueryResponse(TypedDict):
    """Response for contract queries."""

    contracts: List[ContractSummaryDict]


class VerificationSubmissionResponse(TypedDict):
    """Response for proof submission."""

    attempt_id: str
    verdict: str
    matches_claim: bool
    sorry_count: int
    errors: List[str]
    verification_time_ms: int
    unauthorized_dependencies: List[str]


class VerificationAttemptSummary(TypedDict):
    """Summary of a verification attempt."""

    attempt_id: str
    claim_id: int
    submitter_agent_id: str
    verdict: str
    matches_claim: bool
    sorry_count: int
    verification_time_ms: int
    submitted_at: str
    verified_at: str


class VerificationHistoryResponse(TypedDict):
    """Response for verification history."""

    attempts: List[VerificationAttemptSummary]


class PaymentProcessingResponse(TypedDict):
    """Response for payment processing."""

    payment_id: str
    amount: float
    from_agent: str
    to_agent: str
    contract_id: str
    claim_id: int
    signature: str
    timestamp: str
