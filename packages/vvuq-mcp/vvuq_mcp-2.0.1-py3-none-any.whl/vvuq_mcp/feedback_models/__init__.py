"""Pydantic models for vvuq-mcp."""

from .feedback import FeedbackSubmission, FeedbackType, SeverityLevel

# Import core models from sibling models.py file
# (using importlib to avoid circular import due to directory vs file naming conflict)
import sys
from pathlib import Path

# Add parent to path to import models.py
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import from vvuq_mcp.models (the .py file)
try:
    from ..models import (
        Contract,
        ContractClaim,
        ContractRequirements,
        PaymentReceipt,
        ProofSubmission,
        VerificationAttempt,
        VerificationResult,
    )
except ImportError:
    # Fallback for edge cases
    import vvuq_mcp.models as models_module
    Contract = models_module.Contract
    ContractClaim = models_module.ContractClaim
    ContractRequirements = models_module.ContractRequirements
    PaymentReceipt = models_module.PaymentReceipt
    ProofSubmission = models_module.ProofSubmission
    VerificationAttempt = models_module.VerificationAttempt
    VerificationResult = models_module.VerificationResult

__all__ = [
    "FeedbackSubmission",
    "FeedbackType",
    "SeverityLevel",
    "Contract",
    "ContractClaim",
    "ContractRequirements",
    "PaymentReceipt",
    "ProofSubmission",
    "VerificationAttempt",
    "VerificationResult",
]
