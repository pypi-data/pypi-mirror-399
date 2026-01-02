"""
Workspace Manager for VVUQ-MCP.

Handles the lifecycle of Lean 4 workspaces ("Tiered Dependency Management").
- On-demand provisioning of mathlib versions.
- Dynamic generation of lakefile.lean.
- Caching and LRU eviction.

Copyright (c) 2024 Dirk Englund. All rights reserved.
"""

import logging
import asyncio
import shutil
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)

class WorkspaceManager:
    """Manages dynamic Lean 4 workspaces."""

    MAX_CONCURRENT_PROVISIONS = 3
    MAX_TOTAL_WORKSPACES = 50
    # Strict Git tag/commit hash pattern
    MATHLIB_REVISION_PATTERN = re.compile(r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$|^[a-f0-9]{40}$')
    # CamelCase Lean module name, optional :version suffix
    CONTEXT_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*(:v\d+\.\d+\.\d+)?$')

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.workspaces_dir = base_dir / "workspaces"
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)
        self._provision_semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_PROVISIONS)

    def _get_workspace_path(self, revision: str, contexts: List[str]) -> Path:
        """Deterministically generate path from revision string and contexts."""
        # Include sorted contexts in hash to distinguish workspaces
        content = f"{revision}|{sorted(contexts)}"
        # Fix: Increase hash length to 32 chars to reduce collision risk
        rev_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        return self.workspaces_dir / f"mathlib_{rev_hash}"

    async def get_workspace(self, mathlib_revision: str, contexts: List[str] = []) -> Path:
        """
        Get path to a ready-to-use workspace for the given mathlib revision and contexts.
        Provisions it if it doesn't exist.
        """
        path = self._get_workspace_path(mathlib_revision, contexts)
        
        if path.exists() and (path / "lakefile.lean").exists():
            # Security: Verify integrity of existing workspace
            ctx_file = path / ".vvuq_contexts"
            if ctx_file.exists():
                stored_contexts = ctx_file.read_text().splitlines()
                if set(stored_contexts) != set(contexts):
                    logger.warning(f"Context mismatch for {path}, reprovisioning")
                    shutil.rmtree(path)
                else:
                    path.touch()
                    return path
            else:
                 # Legacy/Corrupt workspace
                 shutil.rmtree(path)
        
        # Check total workspace count (Resource Limit)
        existing = sum(1 for p in self.workspaces_dir.iterdir() if p.is_dir())
        if existing >= self.MAX_TOTAL_WORKSPACES:
            # Try cleanup first
            self.cleanup_old_workspaces(max_age_hours=1)
            # Check again
            existing = sum(1 for p in self.workspaces_dir.iterdir() if p.is_dir())
            if existing >= self.MAX_TOTAL_WORKSPACES:
                raise RuntimeError("Workspace limit reached")

        logger.info(f"Provisioning new workspace for {mathlib_revision} (ctx={len(contexts)}) at {path}")
        
        async with self._provision_semaphore:
            if not path.exists():
                await self._provision_workspace(path, mathlib_revision, contexts)
        
        return path

    async def _provision_workspace(self, path: Path, revision: str, contexts: List[str]) -> None:
        """Create and initialize a new workspace."""
        # Security: Validate mathlib revision (Command Injection)
        if not self.MATHLIB_REVISION_PATTERN.match(revision):
             raise ValueError(f"Security Violation: Invalid mathlib_revision format: {revision}")

        path.mkdir(parents=True, exist_ok=True)
        
        # Write context lock file (Integrity)
        (path / ".vvuq_contexts").write_text('\n'.join(sorted(contexts)))

        # 1. Create lakefile.lean
        lakefile_content = f"""
import Lake
open Lake DSL

package «vvuq-verification» {{
  -- add package configuration options here
}}

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "{revision}"

@[default_target]
lean_lib «VvuqVerification» {{
  -- add library configuration options here
}}

lean_lib «Contexts» {{
  srcDir := "Contexts"
}}
"""
        with open(path / "lakefile.lean", "w") as f:
            f.write(lakefile_content)

        # Create Contexts directory and copy files
        if contexts:
            context_dest = path / "Contexts"
            context_dest.mkdir(exist_ok=True)
            context_base = Path(__file__).parent / "data" / "contexts"
            
            for ctx in contexts:
                # Security: Validate context format (Context or Context:Version)
                if not self.CONTEXT_PATTERN.match(ctx):
                    shutil.rmtree(path)
                    raise ValueError(f"Security Violation: Invalid context format: {ctx}")

                # DOI Versioning Logic
                if ":" in ctx:
                    name, version = ctx.split(":", 1)
                    # Mapping: Physics:v1.0.0 -> Physics_v1.0.0.lean
                    filename = f"{name}_{version}.lean"
                    target_name = f"{name}.lean" # In workspace, it is just Name.lean
                else:
                    name = ctx.removesuffix(".lean")
                    filename = f"{name}.lean"
                    target_name = f"{name}.lean"

                # Security: Path Traversal Check
                src_file = (context_base / filename).resolve()
                if not src_file.is_relative_to(context_base.resolve()):
                    shutil.rmtree(path)
                    raise ValueError(f"Security Violation: Path traversal in context: {ctx}")
                
                if src_file.exists():
                     shutil.copy(src_file, context_dest / target_name)
                else:
                     logger.warning(f"Context module {ctx} not found at {src_file}")
                     shutil.rmtree(path)
                     raise ValueError(f"Requested context '{ctx}' (file: {filename}) not found on server.")

        # 2. Create minimal file structure
        (path / "VvuqVerification.lean").touch()
        lean_toolchain = "leanprover/lean4:v4.15.0" 
        with open(path / "lean-toolchain", "w") as f:
            f.write(lean_toolchain)

        # 3. Run 'lake update'
        logger.info("Running lake update...")
        proc = await asyncio.create_subprocess_exec(
            "lake", "update",
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"Failed to update lake: {stderr.decode()}")
            shutil.rmtree(path)
            raise RuntimeError(f"Failed to provision workspace: {stderr.decode()}")

        # 4. Run 'lake exe cache get'
        logger.info("Running lake exe cache get...")
        proc = await asyncio.create_subprocess_exec(
            "lake", "exe", "cache", "get",
            cwd=str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        logger.info(f"Workspace {path} ready.")

    def cleanup_old_workspaces(self, max_age_hours: int = 24) -> int:
        """Delete workspaces accessed > max_age_hours ago."""
        count = 0
        now = datetime.now().timestamp()
        limit = max_age_hours * 3600
        
        for p in self.workspaces_dir.iterdir():
            if p.is_dir() and p.name.startswith("mathlib_"):
                mtime = p.stat().st_mtime
                if now - mtime > limit:
                    logger.info(f"Evicting old workspace: {p}")
                    shutil.rmtree(p)
                    count += 1
        return count
