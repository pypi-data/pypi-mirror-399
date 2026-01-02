"""
Workspace management components for VVUQ-MCP.

This package contains refactored, single-responsibility classes for managing
Lean4 workspaces. The main WorkspaceManager class is a facade coordinating these components.

Components:
- WorkspacePathGenerator: Deterministic path generation
- LakefileGenerator: Lakefile.lean content generation
- ContextCopier: Versioned context file management
- WorkspaceCache: LRU cache and eviction
- WorkspaceProvisioner: Workspace provisioning orchestration
- WorkspaceManager: Legacy monolithic manager (backward compatibility)
"""

from vvuq_mcp.workspaces.path_generator import WorkspacePathGenerator
from vvuq_mcp.workspaces.lakefile_generator import LakefileGenerator
from vvuq_mcp.workspaces.context_copier import ContextCopier
from vvuq_mcp.workspaces.workspace_cache import WorkspaceCache
from vvuq_mcp.workspaces.provisioner import WorkspaceProvisioner

# Import legacy WorkspaceManager for backward compatibility
from vvuq_mcp.workspace_manager_legacy import WorkspaceManager

__all__ = [
    "WorkspacePathGenerator",
    "LakefileGenerator",
    "ContextCopier",
    "WorkspaceCache",
    "WorkspaceProvisioner",
    "WorkspaceManager",  # Legacy
]
