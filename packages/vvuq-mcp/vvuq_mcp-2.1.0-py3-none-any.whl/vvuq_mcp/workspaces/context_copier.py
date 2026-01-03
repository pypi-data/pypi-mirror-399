"""
Context Copier.

Copies versioned context files to workspaces with security validation
and integrity verification.
"""
import re
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class ContextCopier:
    """Copy versioned context files to workspaces with security checks."""

    # CamelCase Lean module name, optional :version suffix
    CONTEXT_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*(:v\d+\.\d+\.\d+)?$')

    def __init__(self, context_storage_dir: Path):
        """
        Initialize context copier.

        Args:
            context_storage_dir: Directory containing context .lean files
        """
        self.context_storage = context_storage_dir
        self.context_storage.mkdir(parents=True, exist_ok=True)

    def _parse_context_version(self, ctx: str) -> Tuple[str, Optional[str]]:
        """
        Parse 'Context:Version' or 'Context' format.

        Args:
            ctx: Context string (e.g., "Physics:v1.0.0" or "Physics")

        Returns:
            Tuple of (name, version) where version is None if not specified
        """
        if ":" in ctx:
            name, version = ctx.split(":", 1)
            return name, version
        return ctx, None

    def _get_source_filename(self, name: str, version: Optional[str]) -> str:
        """
        Map context to source filename.

        Args:
            name: Context name (e.g., "Physics")
            version: Context version (e.g., "v1.0.0") or None

        Returns:
            Source filename (e.g., "Physics_v1.0.0.lean" or "Physics.lean")
        """
        if version:
            # Physics:v1.0.0 -> Physics_v1.0.0.lean
            return f"{name}_{version}.lean"
        return f"{name}.lean"

    def copy_contexts(
        self,
        workspace_contexts_dir: Path,
        contexts: List[str]
    ) -> None:
        """
        Copy context files to workspace with security validation.

        Args:
            workspace_contexts_dir: Destination Contexts/ directory in workspace
            contexts: List of context specifications

        Raises:
            ValueError: If context format invalid, path traversal detected,
                       or context file not found
        """
        if not contexts:
            return

        workspace_contexts_dir.mkdir(parents=True, exist_ok=True)

        for ctx in contexts:
            # Security: Validate format
            if not self.CONTEXT_PATTERN.match(ctx):
                raise ValueError(f"Security Violation: Invalid context format: {ctx}")

            name, version = self._parse_context_version(ctx)
            filename = self._get_source_filename(name, version)

            # Security: Path traversal check
            src_file = (self.context_storage / filename).resolve()
            if not src_file.is_relative_to(self.context_storage.resolve()):
                raise ValueError(f"Security Violation: Path traversal in context: {ctx}")

            if not src_file.exists():
                raise ValueError(f"Context '{ctx}' (file: {filename}) not found on server.")

            # Copy with name normalization
            # (Physics:v1.0.0 -> Physics.lean in workspace)
            dest_file = workspace_contexts_dir / f"{name}.lean"
            shutil.copy(src_file, dest_file)
            logger.debug(f"Copied context: {ctx} ({filename} -> {dest_file.name})")
