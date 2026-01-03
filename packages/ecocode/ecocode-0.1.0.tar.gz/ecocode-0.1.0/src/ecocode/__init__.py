"""EcoCode - AI-powered Python code auditor for environmental efficiency."""

from .models import (
    IssueCategory,
    LoopIssueType,
    MLIssueType,
    Severity,
    Issue,
    ScoreBreakdown,
    RefactorPlan,
    AnalysisResult,
    FileEvent,
)
from .scoring import ScoreCalculator
from .analysis import PatternAnalyzer, NestedLoopDetector, PatternDetector
from .refactoring import RefactorPlanner
from .auditor import EcoCodeAuditor
from .reporter import Reporter

__version__ = "0.1.0"

__all__ = [
    "IssueCategory",
    "LoopIssueType",
    "MLIssueType",
    "Severity",
    "Issue",
    "ScoreBreakdown",
    "RefactorPlan",
    "AnalysisResult",
    "FileEvent",
    "ScoreCalculator",
    "PatternAnalyzer",
    "NestedLoopDetector",
    "PatternDetector",
    "RefactorPlanner",
    "EcoCodeAuditor",
    "Reporter",
]
