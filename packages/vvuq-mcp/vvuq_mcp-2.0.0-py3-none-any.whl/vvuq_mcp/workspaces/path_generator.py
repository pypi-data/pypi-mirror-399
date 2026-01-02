"""
Workspace Path Generator.

Generates deterministic, collision-resistant paths for Lean4 workspaces
based on mathlib revision and context list.
"""
import hashlib
from pathlib import Path
from typing import List


class WorkspacePathGenerator:
    """Generate deterministic, collision-resistant workspace paths."""

    HASH_LENGTH = 32  # 128 bits for collision resistance

    def __init__(self, base_dir: Path):
        """
        Initialize path generator.

        Args:
            base_dir: Base directory for all workspaces
        """
        self.workspaces_dir = base_dir / "workspaces"
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)

    def generate_path(self, revision: str, contexts: List[str]) -> Path:
        """
        Generate deterministic path from revision and contexts.

        The path is order-independent for contexts (sorted internally).
        Uses 128-bit SHA256 hash for collision resistance.

        Args:
            revision: Mathlib git revision (tag or commit hash)
            contexts: List of context names (optionally versioned)

        Returns:
            Path to workspace directory

        Examples:
            >>> gen = WorkspacePathGenerator(Path("/tmp"))
            >>> gen.generate_path("v4.15.0", [])
            Path("/tmp/workspaces/mathlib_a1b2c3...")

            >>> gen.generate_path("v4.15.0", ["Physics:v1.0.0"])
            Path("/tmp/workspaces/mathlib_d4e5f6...")
        """
        # Sort contexts for order-independence
        content = f"{revision}|{sorted(contexts)}"

        # Generate 128-bit hash (32 hex chars)
        path_hash = hashlib.sha256(content.encode()).hexdigest()[:self.HASH_LENGTH]

        return self.workspaces_dir / f"mathlib_{path_hash}"
