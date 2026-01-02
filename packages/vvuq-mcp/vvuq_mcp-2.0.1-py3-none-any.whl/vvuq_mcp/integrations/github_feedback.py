"""
GitHub feedback integration for vvuq-mcp.

Automatically creates GitHub issues from feedback submissions using gh CLI.
Based on patterns from neo4j-memory-mcp and mcp-marketplace.
"""

import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vvuq_mcp.feedback_models.feedback import FeedbackType, SeverityLevel

logger = logging.getLogger(__name__)


class GitHubFeedbackIntegration:
    """
    Handles automatic GitHub issue creation from feedback submissions.

    Uses gh CLI for authentication and issue creation, following the pattern
    established by neo4j-memory-mcp and mcp-marketplace.
    """

    def __init__(self, repo_owner: str, repo_name: str):
        """
        Initialize GitHub feedback integration.

        Args:
            repo_owner: GitHub repository owner (e.g., "dirkenglund")
            repo_name: GitHub repository name (e.g., "vvuq-mcp")
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        # Setup feedback logging directory
        feedback_dir = Path.home() / ".claude" / "vvuq_mcp_feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_log_file = feedback_dir / "submissions.jsonl"

        logger.info(
            f"GitHubFeedbackIntegration initialized for {repo_owner}/{repo_name}"
        )

    def create_feedback_issue(
        self,
        title: str,
        description: str,
        feedback_type: FeedbackType = FeedbackType.GENERAL,
        severity: SeverityLevel = SeverityLevel.MEDIUM,
        tool_name: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        reproduction_steps: Optional[str] = None,
        test_criteria: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue from feedback submission.

        Args:
            title: Issue title
            description: Detailed description
            feedback_type: Type of feedback (bug, feature_request, etc.)
            severity: Severity level (critical, high, medium, low)
            tool_name: Name of the tool that generated feedback
            actual_behavior: What actually happened (for bugs)
            expected_behavior: What should have happened (for bugs)
            reproduction_steps: Steps to reproduce the issue
            test_criteria: How to verify the fix works

        Returns:
            Dict with success status, issue URL, and issue number
        """
        # Format issue body
        body = self._format_issue_body(
            title=title,
            description=description,
            feedback_type=feedback_type,
            severity=severity,
            tool_name=tool_name,
            actual_behavior=actual_behavior,
            expected_behavior=expected_behavior,
            reproduction_steps=reproduction_steps,
            test_criteria=test_criteria,
        )

        # Get labels
        labels = self._get_issue_labels(feedback_type, severity, tool_name)

        # Create GitHub issue
        github_result = self._create_github_issue(title, body, labels)

        # Log submission
        feedback_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "feedback_type": feedback_type.value,
            "severity": severity.value,
            "tool_name": tool_name,
            "github_result": github_result,
        }
        self._log_feedback_submission(feedback_data)

        return github_result

    def _format_issue_body(
        self,
        title: str,
        description: str,
        feedback_type: FeedbackType,
        severity: SeverityLevel,
        tool_name: Optional[str],
        actual_behavior: Optional[str],
        expected_behavior: Optional[str],
        reproduction_steps: Optional[str],
        test_criteria: Optional[str],
    ) -> str:
        """
        Format the issue body in markdown.

        Returns comprehensive markdown with all feedback details.
        """
        sections = [
            f"## VVUQ-MCP {feedback_type.value}",
            "",
            "### Description",
            description,
            "",
            "### Metadata",
            f"- **MCP Server:** vvuq-mcp",
            f"- **Type:** {feedback_type.value}",
            f"- **Severity:** {severity.value}",
        ]

        if tool_name:
            sections.append(f"- **Tool:** {tool_name}")

        sections.extend([
            f"- **Submitted:** {datetime.now(timezone.utc).isoformat()}",
            "- **Auto-generated:** Yes",
            "",
        ])

        # Bug-specific details
        if feedback_type == FeedbackType.BUG:
            if actual_behavior or expected_behavior or reproduction_steps:
                sections.append("### Bug Details")

            if actual_behavior:
                sections.extend([
                    f"**Actual Behavior:** {actual_behavior}",
                    "",
                ])

            if expected_behavior:
                sections.extend([
                    f"**Expected Behavior:** {expected_behavior}",
                    "",
                ])

            if reproduction_steps:
                sections.extend([
                    "**Reproduction Steps:**",
                    reproduction_steps,
                    "",
                ])

        # Test criteria
        if test_criteria:
            sections.extend([
                "### Verification Criteria",
                test_criteria,
                "",
            ])

        # Environment info
        sections.extend([
            "### Environment",
            f"- **Python Version:** {sys.version.split()[0]}",
            f"- **OS:** {platform.system()}",
            f"- **Platform:** {platform.platform()}",
            "",
        ])

        # Next steps checklist
        sections.extend([
            "### Next Steps",
            "- [ ] Triage and assign priority",
            "- [ ] Analyze root cause",
            "- [ ] Implement fix/enhancement",
            "- [ ] Test and validate",
            "- [ ] Update documentation if needed",
        ])

        return "\n".join(sections)

    def _get_issue_labels(
        self,
        feedback_type: FeedbackType,
        severity: SeverityLevel,
        tool_name: Optional[str] = None,
    ) -> List[str]:
        """
        Generate appropriate labels for the issue.

        Returns list of label strings based on feedback type and severity.
        """
        labels = ["vvuq-mcp", "auto-generated", "mcp-feedback"]

        # Type-based labels
        type_label_map = {
            FeedbackType.BUG: ["bug", "needs-fix"],
            FeedbackType.FEATURE_REQUEST: ["enhancement", "feature-request"],
            FeedbackType.IMPROVEMENT: ["enhancement", "improvement"],
            FeedbackType.PERFORMANCE: ["performance", "optimization"],
            FeedbackType.DOCUMENTATION: ["documentation"],
            FeedbackType.SECURITY: ["security", "high-priority"],
            FeedbackType.USABILITY: ["ux", "usability"],
        }

        labels.extend(type_label_map.get(feedback_type, []))

        # Severity-based labels
        severity_label_map = {
            SeverityLevel.CRITICAL: ["P0"],
            SeverityLevel.HIGH: ["high-priority", "P1"],
            SeverityLevel.MEDIUM: ["P2"],
            SeverityLevel.LOW: ["low-priority", "P3"],
        }

        labels.extend(severity_label_map.get(severity, []))

        # Tool-specific label
        if tool_name:
            tool_label = f"tool-{tool_name.lower().replace('_', '-')}"
            labels.append(tool_label)

        return labels

    def _create_github_issue(
        self, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue using gh CLI.

        Args:
            title: Issue title
            body: Issue body (markdown)
            labels: List of label strings

        Returns:
            Dict with success, issue_url, issue_number, or error
        """
        labels_str = ",".join(labels)

        cmd = [
            "gh",
            "issue",
            "create",
            "--repo",
            f"{self.repo_owner}/{self.repo_name}",
            "--title",
            title,
            "--body",
            body,
            "--label",
            labels_str,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=dict(os.environ, GH_HOST="github.com"),
            )

            if result.returncode == 0:
                issue_url = result.stdout.strip()
                issue_number = int(issue_url.split("/")[-1])

                logger.info(f"Created GitHub issue: {issue_url}")
                return {
                    "success": True,
                    "issue_url": issue_url,
                    "issue_number": issue_number,
                }
            else:
                # Retry without labels if label creation fails
                if "not found" in result.stderr.lower():
                    logger.warning("Labels not found, retrying without labels")
                    cmd_no_labels = cmd[:-2]  # Remove --label and labels_str
                    result = subprocess.run(
                        cmd_no_labels,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        env=dict(os.environ, GH_HOST="github.com"),
                    )

                    if result.returncode == 0:
                        issue_url = result.stdout.strip()
                        issue_number = int(issue_url.split("/")[-1])

                        logger.info(f"Created GitHub issue (no labels): {issue_url}")
                        return {
                            "success": True,
                            "issue_url": issue_url,
                            "issue_number": issue_number,
                        }

                logger.error(f"Failed to create GitHub issue: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            error_msg = "GitHub issue creation timed out (30s)"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        except FileNotFoundError:
            error_msg = "gh CLI not installed. Install from: https://cli.github.com/"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Unexpected error creating GitHub issue: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _log_feedback_submission(self, feedback_data: Dict[str, Any]) -> None:
        """
        Log feedback submission to JSONL file for analytics.

        Args:
            feedback_data: Dictionary containing feedback details
        """
        try:
            with open(self.feedback_log_file, "a") as f:
                f.write(json.dumps(feedback_data) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log feedback submission: {e}")

    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get feedback submission statistics.

        Returns:
            Dict with total submissions, breakdowns by type/severity, success rate
        """
        if not self.feedback_log_file.exists():
            return {
                "total_submissions": 0,
                "by_type": {},
                "by_severity": {},
                "success_rate": 0.0,
            }

        submissions = []
        with open(self.feedback_log_file, "r") as f:
            for line in f:
                try:
                    submissions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not submissions:
            return {
                "total_submissions": 0,
                "by_type": {},
                "by_severity": {},
                "success_rate": 0.0,
            }

        # Aggregate statistics
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        successful = 0

        for submission in submissions:
            feedback_type = submission.get("feedback_type", "unknown")
            severity = submission.get("severity", "unknown")
            github_result = submission.get("github_result", {})

            by_type[feedback_type] = by_type.get(feedback_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

            if github_result.get("success"):
                successful += 1

        return {
            "total_submissions": len(submissions),
            "by_type": by_type,
            "by_severity": by_severity,
            "success_rate": successful / len(submissions) if submissions else 0.0,
        }
