"""Reporter module for EcoCode.

This module implements the Reporter class that formats and outputs
analysis results in JSON and human-readable console formats.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import (
    AnalysisResult,
    Issue,
    IssueCategory,
    LoopIssueType,
    MLIssueType,
    RefactorPlan,
    ScoreBreakdown,
    Severity,
)


class Reporter:
    """Formats and outputs analysis results.
    
    Provides methods to serialize AnalysisResult to JSON for programmatic
    consumption and to format results for human-readable console output.
    """
    
    def to_json(self, result: AnalysisResult) -> str:
        """Format analysis result as JSON.
        
        Serializes all fields including nested objects to valid JSON.
        
        Args:
            result: The analysis result to serialize
            
        Returns:
            JSON string representation of the result
            
        Requirements: 6.4
        """
        data = self._result_to_dict(result)
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def from_json(self, json_str: str) -> AnalysisResult:
        """Deserialize JSON string to AnalysisResult.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            AnalysisResult object
            
        Requirements: 6.4
        """
        data = json.loads(json_str)
        return self._dict_to_result(data)
    
    def _result_to_dict(self, result: AnalysisResult) -> dict[str, Any]:
        """Convert AnalysisResult to dictionary for JSON serialization."""
        return {
            "file_path": str(result.file_path),
            "source_hash": result.source_hash,
            "green_score": self._score_to_dict(result.green_score),
            "issues": [self._issue_to_dict(issue) for issue in result.issues],
            "refactor_plans": [self._plan_to_dict(plan) for plan in result.refactor_plans],
            "analysis_timestamp": result.analysis_timestamp.isoformat(),
            "analysis_duration_ms": result.analysis_duration_ms,
        }
    
    def _dict_to_result(self, data: dict[str, Any]) -> AnalysisResult:
        """Convert dictionary to AnalysisResult."""
        return AnalysisResult(
            file_path=Path(data["file_path"]),
            source_hash=data["source_hash"],
            green_score=self._dict_to_score(data["green_score"]),
            issues=[self._dict_to_issue(issue) for issue in data["issues"]],
            refactor_plans=[self._dict_to_plan(plan) for plan in data["refactor_plans"]],
            analysis_timestamp=datetime.fromisoformat(data["analysis_timestamp"]),
            analysis_duration_ms=data["analysis_duration_ms"],
        )
    
    def _score_to_dict(self, score: ScoreBreakdown) -> dict[str, Any]:
        """Convert ScoreBreakdown to dictionary."""
        return {
            "total_score": score.total_score,
            "loop_penalty": score.loop_penalty,
            "ml_penalty": score.ml_penalty,
            "issue_contributions": score.issue_contributions,
        }
    
    def _dict_to_score(self, data: dict[str, Any]) -> ScoreBreakdown:
        """Convert dictionary to ScoreBreakdown."""
        return ScoreBreakdown(
            total_score=data["total_score"],
            loop_penalty=data["loop_penalty"],
            ml_penalty=data["ml_penalty"],
            issue_contributions=[tuple(item) for item in data["issue_contributions"]],
        )
    
    def _issue_to_dict(self, issue: Issue) -> dict[str, Any]:
        """Convert Issue to dictionary."""
        return {
            "issue_id": issue.issue_id,
            "category": issue.category.value,
            "issue_type": issue.issue_type.value,
            "line_number": issue.line_number,
            "column": issue.column,
            "end_line_number": issue.end_line_number,
            "end_column": issue.end_column,
            "code_snippet": issue.code_snippet,
            "severity": issue.severity.value,
            "description": issue.description,
            "metadata": issue.metadata,
        }
    
    def _dict_to_issue(self, data: dict[str, Any]) -> Issue:
        """Convert dictionary to Issue."""
        category = IssueCategory(data["category"])
        
        # Determine issue type based on category
        if category == IssueCategory.INEFFICIENT_LOOP:
            issue_type = LoopIssueType(data["issue_type"])
        else:
            issue_type = MLIssueType(data["issue_type"])
        
        return Issue(
            issue_id=data["issue_id"],
            category=category,
            issue_type=issue_type,
            line_number=data["line_number"],
            column=data["column"],
            end_line_number=data["end_line_number"],
            end_column=data["end_column"],
            code_snippet=data["code_snippet"],
            severity=Severity(data["severity"]),
            description=data["description"],
            metadata=data.get("metadata", {}),
        )
    
    def _plan_to_dict(self, plan: RefactorPlan) -> dict[str, Any]:
        """Convert RefactorPlan to dictionary."""
        return {
            "issue_id": plan.issue_id,
            "original_code": plan.original_code,
            "suggested_code": plan.suggested_code,
            "explanation": plan.explanation,
            "estimated_time_savings": plan.estimated_time_savings,
            "estimated_carbon_savings": plan.estimated_carbon_savings,
            "priority": plan.priority,
        }
    
    def _dict_to_plan(self, data: dict[str, Any]) -> RefactorPlan:
        """Convert dictionary to RefactorPlan."""
        return RefactorPlan(
            issue_id=data["issue_id"],
            original_code=data["original_code"],
            suggested_code=data["suggested_code"],
            explanation=data["explanation"],
            estimated_time_savings=data["estimated_time_savings"],
            estimated_carbon_savings=data["estimated_carbon_savings"],
            priority=data["priority"],
        )


    def to_console(self, result: AnalysisResult) -> str:
        """Format analysis result for human-readable console output.
        
        Formats the Green Score prominently with color indicators,
        lists issues with locations and severities, and presents
        refactor plans in priority order.
        
        Args:
            result: The analysis result to format
            
        Returns:
            Formatted string for console output
            
        Requirements: 6.1, 6.2, 6.3, 6.5
        """
        lines: list[str] = []
        
        # Header
        lines.append("=" * 60)
        lines.append("EcoCode Analysis Report")
        lines.append("=" * 60)
        lines.append("")
        
        # File info
        lines.append(f"File: {result.file_path}")
        lines.append(f"Analyzed: {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duration: {result.analysis_duration_ms}ms")
        lines.append("")
        
        # Green Score (Requirement 6.1)
        lines.append("-" * 60)
        score = result.green_score.total_score
        score_indicator = self._get_score_indicator(score)
        lines.append(f"GREEN SCORE: {score}/100 {score_indicator}")
        lines.append("-" * 60)
        
        # Score breakdown
        if result.green_score.loop_penalty > 0 or result.green_score.ml_penalty > 0:
            lines.append("")
            lines.append("Score Breakdown:")
            if result.green_score.loop_penalty > 0:
                lines.append(f"  Loop inefficiencies: -{result.green_score.loop_penalty}")
            if result.green_score.ml_penalty > 0:
                lines.append(f"  ML call inefficiencies: -{result.green_score.ml_penalty}")
        
        lines.append("")
        
        # Issues (Requirement 6.2)
        if result.issues:
            lines.append("-" * 60)
            lines.append(f"ISSUES DETECTED: {len(result.issues)}")
            lines.append("-" * 60)
            lines.append("")
            
            for i, issue in enumerate(result.issues, 1):
                severity_icon = self._get_severity_icon(issue.severity)
                lines.append(f"{i}. [{severity_icon}] {issue.description}")
                lines.append(f"   Location: Line {issue.line_number}, Column {issue.column}")
                lines.append(f"   Type: {issue.issue_type.value}")
                lines.append(f"   Severity: {issue.severity.value.upper()}")
                if issue.code_snippet:
                    lines.append(f"   Code: {issue.code_snippet[:50]}{'...' if len(issue.code_snippet) > 50 else ''}")
                lines.append("")
        else:
            lines.append("No issues detected. Great job! 🌱")
            lines.append("")
        
        # Refactor Plans (Requirement 6.3)
        if result.refactor_plans:
            lines.append("-" * 60)
            lines.append("REFACTORING SUGGESTIONS (by priority)")
            lines.append("-" * 60)
            lines.append("")
            
            # Sort by priority (already sorted, but ensure order)
            sorted_plans = sorted(result.refactor_plans, key=lambda p: p.priority)
            
            for plan in sorted_plans:
                lines.append(f"Priority {plan.priority}:")
                lines.append(f"  {plan.explanation}")
                lines.append("")
                lines.append("  Original:")
                for code_line in plan.original_code.split('\n')[:5]:
                    lines.append(f"    {code_line}")
                if plan.original_code.count('\n') > 4:
                    lines.append("    ...")
                lines.append("")
                lines.append("  Suggested:")
                for code_line in plan.suggested_code.split('\n')[:5]:
                    lines.append(f"    {code_line}")
                if plan.suggested_code.count('\n') > 4:
                    lines.append("    ...")
                lines.append("")
                lines.append(f"  Estimated time savings: {plan.estimated_time_savings}")
                lines.append(f"  Estimated carbon savings: {plan.estimated_carbon_savings}")
                lines.append("")
        
        # Footer
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _get_score_indicator(self, score: int) -> str:
        """Get a visual indicator for the score.
        
        Args:
            score: The Green Score (0-100)
            
        Returns:
            Emoji/text indicator based on score range
        """
        if score >= 90:
            return "🌳 Excellent!"
        elif score >= 70:
            return "🌿 Good"
        elif score >= 50:
            return "🌱 Needs Improvement"
        elif score >= 30:
            return "⚠️ Poor"
        else:
            return "🔴 Critical"
    
    def _get_severity_icon(self, severity: Severity) -> str:
        """Get an icon for the severity level.
        
        Args:
            severity: The severity level
            
        Returns:
            Icon string for the severity
        """
        icons = {
            Severity.LOW: "LOW",
            Severity.MEDIUM: "MED",
            Severity.HIGH: "HIGH",
        }
        return icons.get(severity, "???")
