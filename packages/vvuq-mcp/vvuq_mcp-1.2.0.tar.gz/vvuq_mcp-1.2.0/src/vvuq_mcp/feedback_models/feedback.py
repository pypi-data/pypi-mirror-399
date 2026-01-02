"""
Pydantic models for feedback submissions.

Defines the data structures for collecting and validating feedback
before creating GitHub issues.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FeedbackType(str, Enum):
    """Type of feedback being submitted."""

    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    USABILITY = "usability"
    GENERAL = "general"


class SeverityLevel(str, Enum):
    """Severity level of the feedback."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeedbackSubmission(BaseModel):
    """
    Structured feedback submission.

    Used to validate and format feedback before creating GitHub issues.
    """

    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: str = Field(..., min_length=1, description="Detailed description")
    feedback_type: FeedbackType = Field(
        FeedbackType.GENERAL, description="Type of feedback"
    )
    severity: SeverityLevel = Field(
        SeverityLevel.MEDIUM, description="Severity level"
    )
    tool_name: Optional[str] = Field(None, description="Tool that generated feedback")
    actual_behavior: Optional[str] = Field(
        None, description="What actually happened (for bugs)"
    )
    expected_behavior: Optional[str] = Field(
        None, description="What should have happened (for bugs)"
    )
    reproduction_steps: Optional[str] = Field(
        None, description="Steps to reproduce the issue"
    )
    test_criteria: Optional[str] = Field(
        None, description="How to verify the fix works"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Theorem extraction returns None",
                    "description": "Proof compiles successfully but vvuq-mcp returns None for theorem name",
                    "feedback_type": "bug",
                    "severity": "critical",
                    "tool_name": "submit_proof",
                    "actual_behavior": "Returns 'None' for proven_theorem field",
                    "expected_behavior": "Returns actual theorem name from proof",
                    "reproduction_steps": "1. Submit valid Lean4 proof\n2. Check verification result\n3. Observe proven_theorem is None",
                    "test_criteria": "Verification result should include correct theorem name",
                }
            ]
        }
    }
