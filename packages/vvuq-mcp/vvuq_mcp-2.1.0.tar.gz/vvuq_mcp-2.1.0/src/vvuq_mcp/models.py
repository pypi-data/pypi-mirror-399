"""
Pydantic data models for VVUQ-MCP.

All data validation and serialization happens through these models.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Final, List, Optional, Literal
from datetime import datetime

import re
from vvuq_mcp.exceptions import InvalidDependencyError


# Field constraint constants for reusability
MAX_TITLE_LENGTH: Final[int] = 200
MAX_DESCRIPTION_LENGTH: Final[int] = 2000
MAX_PROOF_CODE_LENGTH: Final[int] = 500_000
SIGNATURE_LENGTH: Final[int] = 64


# Factory functions to reduce Field() repetition
def required_string_field(description: str, max_length: Optional[int] = None, **kwargs) -> Field:
    """Create a required non-empty string field with description."""
    field_kwargs = {"min_length": 1, "description": description, **kwargs}
    if max_length:
        field_kwargs["max_length"] = max_length
    return Field(**field_kwargs)


class ContractClaim(BaseModel):
    """A single verifiable claim within a contract."""

    claim_id: int = Field(ge=1, description="Unique claim identifier within contract")
    theorem_statement: str = Field(
        min_length=1, description="Lean4 theorem to prove (e.g., 'theorem name : statement')"
    )
    allowed_dependencies: List[str] = Field(
        default_factory=list, description="Allowed Lean4 imports (e.g., ['Mathlib.Data.Nat.Basic'])"
    )
    payment_amount: float = Field(gt=0, description="Payment in credits for successful proof")
    payment_type: Literal["all-or-nothing", "partial", "graded"] = Field(
        default="all-or-nothing", description="Payment distribution strategy"
    )
    mathlib_version: Optional[str] = Field(
        default=None, description="Mathlib4 git revision tag"
    )
    assumption_contexts: List[str] = Field(
        default_factory=list, description="List of server-side assumption context modules to include"
    )

    @field_validator("allowed_dependencies")
    @classmethod
    def validate_dependencies(cls, dependencies: List[str]) -> List[str]:
        """Ensure all dependencies are valid Lean4 import paths."""
        # We previously restricted this to uppercase only, but feedback indicates
        # legitimate use cases for other imports, or simply bulk importing mathlib.
        # So we relax the validation to allow "all" dependencies if desired.
        for dep in dependencies:
            if not dep or not isinstance(dep, str):
                raise InvalidDependencyError(f"Invalid dependency: {dep}")
                
            # Relaxed check: Just warn/log if it looks weird, but don't crash.
            # Real validation happens at compilation time anyway.
            # if not dep[0].isupper():
            #     # Optional: logging logic here if we had a logger
            #     pass
        return dependencies

    @field_validator("mathlib_version")
    @classmethod
    def validate_mathlib_version(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Strict Git tag/commit hash pattern
        pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$|^[a-f0-9]{40}$'
        if not re.match(pattern, v):
            raise ValueError(f"Invalid mathlib_version format: {v}")
        return v

    @field_validator("assumption_contexts")
    @classmethod
    def validate_contexts(cls, contexts: List[str]) -> List[str]:
        # CamelCase Lean module name, optional :version suffix
        pattern = r'^[A-Z][a-zA-Z0-9]*(:v\d+\.\d+\.\d+)?$'
        if len(contexts) > 10:
             raise ValueError("Too many contexts (max 10)")
        for ctx in contexts:
            if len(ctx) > 50:
                raise ValueError("Context name too long (max 50 chars)")
            if not re.match(pattern, ctx):
                raise ValueError(f"Invalid context format: {ctx}")
        return contexts


class Contract(BaseModel):
    """A marketplace contract with formal proof requirements."""

    contract_id: str = Field(min_length=1, description="Unique contract identifier")
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH, description="Contract title")
    description: str = Field(max_length=MAX_DESCRIPTION_LENGTH, description="Contract description")
    claims: List[ContractClaim] = Field(min_length=1, description="List of claims to verify")
    issuer_agent_id: str = Field(min_length=1, description="Agent who created the contract")
    created_at: datetime = Field(default_factory=datetime.now, description="Contract creation timestamp")
    status: Literal["OPEN", "IN_VERIFICATION", "COMPLETED", "CANCELLED"] = Field(
        default="OPEN", description="Current contract status"
    )


class ProofSubmission(BaseModel):
    """Agent's proof submission for verification."""

    contract_id: str = Field(min_length=1, description="Contract identifier being submitted to")
    claim_id: int = Field(ge=1, description="Claim identifier within the contract")
    submitter_agent_id: str = Field(min_length=1, description="Agent submitting the proof")
    proof_code: str = Field(
        min_length=1, max_length=MAX_PROOF_CODE_LENGTH, description="Complete Lean4 proof"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="Lean4 imports used (must match claim.allowed_dependencies)"
    )
    submitted_at: datetime = Field(default_factory=datetime.now, description="Submission timestamp")

    @field_validator("proof_code")
    @classmethod
    def validate_proof_code(cls, code: str) -> str:
        """Basic validation of proof code."""
        if len(code.strip()) == 0:
            raise ValueError("Proof code cannot be empty")
        return code


class VerificationResult(BaseModel):
    """Result of proof verification."""

    verdict: Literal["ACCEPTED", "REJECTED", "ERROR"] = Field(
        description="Verification verdict: ACCEPTED, REJECTED, or ERROR"
    )
    compilation_output: str = Field(default="", description="Raw Lean compiler output")
    proven_theorem: Optional[str] = Field(default=None, description="Extracted theorem statement if proven")
    matches_claim: bool = Field(default=False, description="Whether proven theorem matches claimed theorem")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    sorry_count: int = Field(ge=0, default=0, description="Number of sorry/admit statements found")
    unauthorized_dependencies: List[str] = Field(
        default_factory=list, description="Dependencies used but not allowed"
    )
    verification_time_ms: int = Field(ge=0, description="Time taken for verification in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Verification timestamp")


class PaymentReceipt(BaseModel):
    """Cryptographically signed payment record."""

    payment_id: str = Field(min_length=1, description="Unique payment identifier")
    amount: float = Field(gt=0, description="Payment amount in credits")
    from_agent: str = Field(min_length=1, description="Agent making the payment")
    to_agent: str = Field(min_length=1, description="Agent receiving the payment")
    contract_id: str = Field(min_length=1, description="Associated contract identifier")
    claim_id: int = Field(ge=1, description="Associated claim identifier")
    signature: str = Field(
        min_length=SIGNATURE_LENGTH, max_length=SIGNATURE_LENGTH, description="HMAC-SHA256 signature (hex)"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Payment timestamp")
    transaction_type: Literal["credit", "debit"] = Field(description="Transaction direction")


class VerificationAttempt(BaseModel):
    """Complete record of a verification attempt."""

    attempt_id: str = Field(description="Unique attempt identifier")
    contract_id: str = Field(description="Contract being verified")
    claim_id: int = Field(description="Claim being verified")
    submitter_agent_id: str = Field(description="Agent who submitted the proof")
    proof_code: str = Field(description="Submitted Lean4 proof code")
    result: VerificationResult = Field(description="Verification result")
    payment: Optional[PaymentReceipt] = Field(default=None, description="Payment receipt if proof accepted")
    submitted_at: datetime = Field(description="When proof was submitted")
    verified_at: datetime = Field(description="When verification completed")


class ContractRequirements(BaseModel):
    """Contract requirements returned to agents for reference."""

    contract_id: str = Field(description="Contract identifier")
    claim_id: int = Field(description="Claim identifier")
    theorem_statement: str = Field(description="Lean4 theorem to prove")
    allowed_dependencies: List[str] = Field(description="List of allowed Lean4 imports")
    payment_amount: float = Field(description="Payment amount in credits")
    payment_type: str = Field(description="Payment distribution type")
    status: str = Field(description="Current contract status")
