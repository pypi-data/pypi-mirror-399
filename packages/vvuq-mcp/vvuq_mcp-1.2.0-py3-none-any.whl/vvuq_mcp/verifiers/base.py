"""
Abstract base class for proof verifiers.

All proof systems (Lean4, Coq, Isabelle) should inherit from this base class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

from vvuq_mcp.models import VerificationResult


class BaseVerifier(ABC):
    """Abstract base class for proof verifiers."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize the verifier.

        Args:
            workspace_dir: Directory for verification operations.
                          Must contain pre-built dependencies (e.g., mathlib cache).
        """
        self.workspace_dir = workspace_dir

    @abstractmethod
    async def verify_proof(
        self,
        proof_code: str,
        expected_theorem: str,
        allowed_dependencies: List[str],
        timeout_seconds: int = 60,
    ) -> VerificationResult:
        """
        Verify a proof against expected theorem.

        Args:
            proof_code: Complete proof code to verify
            expected_theorem: The theorem statement that should be proven
            allowed_dependencies: List of allowed imports/dependencies
            timeout_seconds: Maximum time for verification

        Returns:
            VerificationResult with verdict and details
        """
        pass

    @abstractmethod
    async def check_for_sorry(self, proof_code: str) -> List[int]:
        """
        Check for incomplete proofs (sorry keywords).

        Args:
            proof_code: Proof code to check

        Returns:
            List of line numbers where sorry appears
        """
        pass

    @abstractmethod
    def extract_imports(self, proof_code: str) -> List[str]:
        """
        Extract import statements from proof code.

        Args:
            proof_code: Proof code to parse

        Returns:
            List of import paths
        """
        pass

    @abstractmethod
    async def validate_dependencies(
        self, imports: List[str], allowed: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all imports are in the allowed list.

        Args:
            imports: List of imports found in proof
            allowed: List of allowed imports

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        pass
