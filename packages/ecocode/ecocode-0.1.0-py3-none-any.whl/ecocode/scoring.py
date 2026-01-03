"""Score calculation for EcoCode.

This module implements the Green Score calculation based on detected issues.
The score follows these correctness properties:
- Property 3: Score always in range [0, 100]
- Property 4: Empty issues gives score of 100
- Property 5: Same issues produce same score (determinism)
- Property 6: Higher severity = higher penalty
- Property 7: Sum of penalties + total_score = 100
"""

from .models import Issue, IssueCategory, ScoreBreakdown, Severity

# Severity weights as defined in design
SEVERITY_WEIGHTS: dict[Severity, int] = {
    Severity.LOW: 5,
    Severity.MEDIUM: 10,
    Severity.HIGH: 20,
}

BASE_SCORE = 100


class ScoreCalculator:
    """Calculates the Green Score from detected issues.
    
    The Green Score starts at 100 and decreases based on detected issues.
    Each issue contributes a penalty based on its severity level.
    """
    
    def __init__(self) -> None:
        """Initialize the ScoreCalculator."""
        self._severity_weights = SEVERITY_WEIGHTS
    
    def calculate(self, issues: list[Issue]) -> ScoreBreakdown:
        """Calculate the Green Score from a list of issues.
        
        Args:
            issues: List of detected issues to score
            
        Returns:
            ScoreBreakdown with total score and penalty breakdown
            
        Properties enforced:
            - Property 3: total_score in [0, 100]
            - Property 4: Empty issues returns score of 100
            - Property 5: Deterministic - same issues = same score
            - Property 7: sum(penalties) + total_score = 100
        """
        if not issues:
            return ScoreBreakdown(
                total_score=BASE_SCORE,
                loop_penalty=0,
                ml_penalty=0,
                issue_contributions=[],
            )
        
        loop_penalty = 0
        ml_penalty = 0
        issue_contributions: list[tuple[str, int]] = []
        
        for issue in issues:
            penalty = self._severity_weights[issue.severity]
            issue_contributions.append((issue.issue_id, penalty))
            
            if issue.category == IssueCategory.INEFFICIENT_LOOP:
                loop_penalty += penalty
            elif issue.category == IssueCategory.HEAVY_ML_CALL:
                ml_penalty += penalty
        
        total_penalty = loop_penalty + ml_penalty
        
        # Property 3: Cap score at minimum 0, maximum 100
        total_score = max(0, min(BASE_SCORE, BASE_SCORE - total_penalty))
        
        # Property 7: Ensure breakdown consistency
        # If penalties exceed 100, we need to adjust the breakdown
        # so that penalties + score = 100
        if total_penalty > BASE_SCORE:
            # Scale penalties proportionally to maintain consistency
            scale_factor = BASE_SCORE / total_penalty
            loop_penalty = int(loop_penalty * scale_factor)
            ml_penalty = BASE_SCORE - loop_penalty  # Ensure exact sum
            
            # Recalculate contributions proportionally
            scaled_contributions: list[tuple[str, int]] = []
            remaining = BASE_SCORE
            for i, (issue_id, penalty) in enumerate(issue_contributions):
                if i == len(issue_contributions) - 1:
                    # Last item gets remainder to ensure exact sum
                    scaled_contributions.append((issue_id, remaining))
                else:
                    scaled_penalty = int(penalty * scale_factor)
                    scaled_contributions.append((issue_id, scaled_penalty))
                    remaining -= scaled_penalty
            issue_contributions = scaled_contributions
        
        return ScoreBreakdown(
            total_score=total_score,
            loop_penalty=loop_penalty,
            ml_penalty=ml_penalty,
            issue_contributions=issue_contributions,
        )
