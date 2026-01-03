"""EcoCode CLI entry point.

Provides command-line interface for analyzing Python files for
energy efficiency issues.

Usage:
    python -m ecocode --analyze <file>       # Analyze a single file
    python -m ecocode --watch <directory>    # Monitor directory for changes
    python -m ecocode --analyze <file> --json  # Output as JSON
    python -m ecocode --analyze <file> --output results.json  # Save to file

Requirements: 6.4, 6.5
"""

import argparse
import json
import signal
import sys
from pathlib import Path
from typing import Any

from .auditor import EcoCodeAuditor
from .models import AnalysisResult


def result_to_dict(result: AnalysisResult) -> dict[str, Any]:
    """Convert AnalysisResult to a JSON-serializable dict.
    
    Args:
        result: The analysis result to convert
        
    Returns:
        A dictionary suitable for JSON serialization
        
    Requirements: 6.4
    """
    return {
        "file_path": str(result.file_path),
        "source_hash": result.source_hash,
        "analysis_timestamp": result.analysis_timestamp.isoformat(),
        "analysis_duration_ms": result.analysis_duration_ms,
        "green_score": {
            "total_score": result.green_score.total_score,
            "loop_penalty": result.green_score.loop_penalty,
            "ml_penalty": result.green_score.ml_penalty,
            "issue_contributions": [
                {"issue_id": issue_id, "penalty": penalty}
                for issue_id, penalty in result.green_score.issue_contributions
            ],
        },
        "issues": [
            {
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
            for issue in result.issues
        ],
        "refactor_plans": [
            {
                "issue_id": plan.issue_id,
                "priority": plan.priority,
                "original_code": plan.original_code,
                "suggested_code": plan.suggested_code,
                "explanation": plan.explanation,
                "estimated_time_savings": plan.estimated_time_savings,
                "estimated_carbon_savings": plan.estimated_carbon_savings,
            }
            for plan in result.refactor_plans
        ],
    }


def format_console_output(result: AnalysisResult) -> str:
    """Format analysis result for human-readable console output.
    
    Args:
        result: The analysis result to format
        
    Returns:
        A formatted string for console display
        
    Requirements: 6.5
    """
    lines: list[str] = []
    score = result.green_score.total_score
    
    # Color indicators based on score
    if score >= 80:
        score_indicator = "🟢"
    elif score >= 50:
        score_indicator = "🟡"
    else:
        score_indicator = "🔴"
    
    # Header with Green Score
    lines.append("=" * 60)
    lines.append(f"  EcoCode Analysis Report")
    lines.append(f"  File: {result.file_path}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  {score_indicator} Green Score: {score}/100")
    lines.append("")
    
    # Score breakdown
    if result.green_score.loop_penalty > 0 or result.green_score.ml_penalty > 0:
        lines.append("  Score Breakdown:")
        if result.green_score.loop_penalty > 0:
            lines.append(f"    - Loop inefficiencies: -{result.green_score.loop_penalty}")
        if result.green_score.ml_penalty > 0:
            lines.append(f"    - ML inefficiencies: -{result.green_score.ml_penalty}")
        lines.append("")
    
    # Issues section
    if result.issues:
        lines.append("-" * 60)
        lines.append(f"  Issues Found: {len(result.issues)}")
        lines.append("-" * 60)
        lines.append("")
        
        for i, issue in enumerate(result.issues, 1):
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                issue.severity.value, "⚪"
            )
            lines.append(f"  {i}. [{severity_icon} {issue.severity.value.upper()}] {issue.issue_type.value}")
            lines.append(f"     Line {issue.line_number}, Column {issue.column}")
            lines.append(f"     {issue.description}")
            lines.append("")
    else:
        lines.append("-" * 60)
        lines.append("  ✅ No issues found! Your code is efficient.")
        lines.append("-" * 60)
        lines.append("")
    
    # Refactor plans section
    if result.refactor_plans:
        lines.append("-" * 60)
        lines.append("  Refactoring Suggestions (by priority):")
        lines.append("-" * 60)
        lines.append("")
        
        for plan in result.refactor_plans:
            lines.append(f"  Priority {plan.priority}: Issue {plan.issue_id[:8]}...")
            lines.append(f"    ⏱️  Time savings: {plan.estimated_time_savings}")
            lines.append(f"    🌱 Carbon savings: {plan.estimated_carbon_savings}")
            lines.append(f"    💡 {plan.explanation[:100]}...")
            lines.append("")
    
    lines.append("=" * 60)
    lines.append(f"  Analysis completed in {result.analysis_duration_ms}ms")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def handle_analysis_result(result: AnalysisResult) -> None:
    """Handle analysis result during watch mode.
    
    Args:
        result: The analysis result to display
    """
    print("\n" + format_console_output(result))


def main() -> int:
    """Main entry point for EcoCode CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        prog="ecocode",
        description="EcoCode - AI-powered Python code auditor for energy efficiency",
        epilog="Examples:\n"
               "  ecocode --analyze script.py\n"
               "  ecocode --analyze script.py --json\n"
               "  ecocode --analyze script.py --output results.json\n"
               "  ecocode --watch ./src",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Mutually exclusive group for analyze vs watch
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--analyze",
        type=Path,
        metavar="FILE",
        help="Path to Python file to analyze",
    )
    mode_group.add_argument(
        "--watch",
        type=Path,
        metavar="DIRECTORY",
        help="Directory to monitor for Python file changes",
    )
    
    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (console output)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        metavar="FILE",
        help="Save JSON results to file",
    )
    
    args = parser.parse_args()
    auditor = EcoCodeAuditor()
    
    if args.analyze:
        # Single file analysis mode
        if not args.analyze.exists():
            print(f"Error: File not found: {args.analyze}", file=sys.stderr)
            return 1
        
        if not args.analyze.is_file():
            print(f"Error: Not a file: {args.analyze}", file=sys.stderr)
            return 1
        
        try:
            result = auditor.analyze_file(args.analyze)
        except Exception as e:
            print(f"Error analyzing file: {e}", file=sys.stderr)
            return 1
        
        # Output results
        if args.json:
            print(json.dumps(result_to_dict(result), indent=2))
        else:
            print(format_console_output(result))
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result_to_dict(result), f, indent=2)
                print(f"\nResults saved to: {args.output}")
            except Exception as e:
                print(f"Error saving results: {e}", file=sys.stderr)
                return 1
        
        return 0
    
    elif args.watch:
        # Directory monitoring mode
        if not args.watch.exists():
            print(f"Error: Directory not found: {args.watch}", file=sys.stderr)
            return 1
        
        if not args.watch.is_dir():
            print(f"Error: Not a directory: {args.watch}", file=sys.stderr)
            return 1
        
        print(f"Starting EcoCode monitor on: {args.watch}")
        print("Press Ctrl+C to stop monitoring.\n")
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig: int, frame: Any) -> None:
            print("\nStopping monitor...")
            auditor.stop_monitoring()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            auditor.start_monitoring(args.watch, callback=handle_analysis_result)
            # Keep the main thread alive
            signal.pause()
        except NotImplementedError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error starting monitor: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
