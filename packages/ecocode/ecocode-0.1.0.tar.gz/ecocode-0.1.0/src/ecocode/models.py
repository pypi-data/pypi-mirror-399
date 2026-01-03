"""Core data models for EcoCode.

This module defines the enums and dataclasses used throughout EcoCode
for representing issues, scores, refactoring plans, and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class IssueCategory(Enum):
    """Categories of code efficiency issues."""
    INEFFICIENT_LOOP = "inefficient_loop"
    HEAVY_ML_CALL = "heavy_ml_call"


class LoopIssueType(Enum):
    """Types of inefficient loop patterns."""
    NESTED_VECTORIZABLE = "nested_vectorizable"
    REDUNDANT_COMPUTATION = "redundant_computation"
    UNBATCHED_ITERATION = "unbatched_iteration"


class MLIssueType(Enum):
    """Types of heavy ML model call patterns."""
    MODEL_LOADING_IN_LOOP = "model_loading_in_loop"
    UNBATCHED_INFERENCE = "unbatched_inference"
    UNUSED_MODEL_OUTPUT = "unused_model_output"


class Severity(Enum):
    """Severity levels for detected issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Issue:
    """Represents a detected code efficiency issue.
    
    Attributes:
        issue_id: Unique identifier for the issue (UUID)
        category: The category of the issue (loop or ML)
        issue_type: Specific type of the issue within its category
        line_number: Starting line number where the issue was detected
        column: Starting column number
        end_line_number: Ending line number of the issue
        end_column: Ending column number
        code_snippet: The problematic code snippet
        severity: Severity level of the issue
        description: Human-readable description of the issue
        metadata: Additional pattern-specific data
    """
    issue_id: str
    category: IssueCategory
    issue_type: LoopIssueType | MLIssueType
    line_number: int
    column: int
    end_line_number: int
    end_column: int
    code_snippet: str
    severity: Severity
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoreBreakdown:
    """Breakdown of the Green Score calculation.
    
    Attributes:
        total_score: The final Green Score (0-100)
        loop_penalty: Total penalty from inefficient loop issues
        ml_penalty: Total penalty from heavy ML call issues
        issue_contributions: List of (issue_id, penalty) tuples showing
                           how each issue contributed to the score reduction
    """
    total_score: int
    loop_penalty: int
    ml_penalty: int
    issue_contributions: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class RefactorPlan:
    """A refactoring suggestion for a detected issue.
    
    Attributes:
        issue_id: ID of the issue this plan addresses
        original_code: The original problematic code
        suggested_code: The suggested refactored code
        explanation: Human-readable explanation of the improvement
        estimated_time_savings: Estimated performance improvement (e.g., "2-5x faster")
        estimated_carbon_savings: Estimated carbon reduction (e.g., "~40% reduction")
        priority: Priority ranking (1 = highest priority)
    """
    issue_id: str
    original_code: str
    suggested_code: str
    explanation: str
    estimated_time_savings: str
    estimated_carbon_savings: str
    priority: int


@dataclass
class AnalysisResult:
    """Complete result of analyzing a Python file.
    
    Attributes:
        file_path: Path to the analyzed file
        source_hash: SHA256 hash of the analyzed source code
        green_score: The calculated Green Score with breakdown
        issues: List of detected issues
        refactor_plans: List of refactoring suggestions
        analysis_timestamp: When the analysis was performed
        analysis_duration_ms: How long the analysis took in milliseconds
    """
    file_path: Path
    source_hash: str
    green_score: ScoreBreakdown
    issues: list[Issue]
    refactor_plans: list[RefactorPlan]
    analysis_timestamp: datetime
    analysis_duration_ms: int


@dataclass
class FileEvent:
    """Represents a file system event for a monitored file.
    
    Attributes:
        path: Path to the file that triggered the event
        event_type: Type of event ("saved", "created", "modified")
        timestamp: When the event occurred
    """
    path: Path
    event_type: str
    timestamp: datetime
