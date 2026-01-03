"""EcoCode CLI entry point (legacy).

This module provides backward compatibility. The main CLI is now in __main__.py.
Use `python -m ecocode` for the full CLI experience.

For programmatic use, import EcoCodeAuditor from ecocode.auditor.
"""

from pathlib import Path

from .auditor import EcoCodeAuditor
from .models import AnalysisResult


def analyze_file(file_path: Path) -> AnalysisResult:
    """Analyze a Python file for efficiency issues.
    
    This is a convenience function that creates an EcoCodeAuditor
    and analyzes a single file.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        AnalysisResult with issues, score, and refactor plans
    """
    auditor = EcoCodeAuditor()
    return auditor.analyze_file(file_path)


# Re-export main from __main__ for backward compatibility
def main() -> int:
    """Main entry point for EcoCode CLI."""
    from .__main__ import main as cli_main
    return cli_main()


if __name__ == "__main__":
    import sys
    sys.exit(main())
