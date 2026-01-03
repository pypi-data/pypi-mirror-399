"""
Workspace Cache.

Manages workspace cache with LRU (Least Recently Used) eviction policy.
"""
import shutil
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkspaceCache:
    """Manage workspace cache with LRU eviction."""

    def __init__(self, workspaces_dir: Path):
        """
        Initialize workspace cache.

        Args:
            workspaces_dir: Directory containing workspace subdirectories
        """
        self.workspaces_dir = workspaces_dir
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)

    def update_access_time(self, workspace_path: Path) -> None:
        """
        Touch workspace to update access time (LRU tracking).

        Args:
            workspace_path: Path to workspace directory
        """
        workspace_path.touch()

    def evict_old_workspaces(self, max_age_hours: int = 24) -> int:
        """
        Delete workspaces accessed > max_age_hours ago.

        Args:
            max_age_hours: Maximum age in hours before eviction

        Returns:
            Number of workspaces deleted
        """
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

    def count_workspaces(self) -> int:
        """
        Count existing mathlib workspaces.

        Returns:
            Number of workspace directories
        """
        return sum(
            1 for p in self.workspaces_dir.iterdir()
            if p.is_dir() and p.name.startswith("mathlib_")
        )
