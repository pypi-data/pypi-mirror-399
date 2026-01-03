"""Refactoring plan generation for EcoCode.

This module implements the RefactorPlanner that generates refactoring
suggestions for detected code efficiency issues.

Properties enforced:
- Property 8: All plans have required fields (non-empty values)
- Property 9: Plans sorted by priority (1 = highest priority first)
- Property 14: One RefactorPlan per Issue (plan count equals issue count)
"""

from .models import Issue, IssueCategory, LoopIssueType, MLIssueType, RefactorPlan, Severity


# Priority mapping: higher severity = higher priority (lower number)
SEVERITY_PRIORITY: dict[Severity, int] = {
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
}

# Estimated time savings by issue type
TIME_SAVINGS: dict[LoopIssueType | MLIssueType, str] = {
    # Loop issues
    LoopIssueType.NESTED_VECTORIZABLE: "10-100x faster",
    LoopIssueType.REDUNDANT_COMPUTATION: "2-5x faster",
    LoopIssueType.UNBATCHED_ITERATION: "2-10x faster",
    # ML issues
    MLIssueType.MODEL_LOADING_IN_LOOP: "100-1000x faster",
    MLIssueType.UNBATCHED_INFERENCE: "5-50x faster",
    MLIssueType.UNUSED_MODEL_OUTPUT: "Eliminates wasted computation",
}

# Estimated carbon savings by issue type
CARBON_SAVINGS: dict[LoopIssueType | MLIssueType, str] = {
    # Loop issues
    LoopIssueType.NESTED_VECTORIZABLE: "~90% reduction",
    LoopIssueType.REDUNDANT_COMPUTATION: "~60% reduction",
    LoopIssueType.UNBATCHED_ITERATION: "~70% reduction",
    # ML issues
    MLIssueType.MODEL_LOADING_IN_LOOP: "~99% reduction",
    MLIssueType.UNBATCHED_INFERENCE: "~80% reduction",
    MLIssueType.UNUSED_MODEL_OUTPUT: "~100% reduction for this call",
}


# Refactoring templates for each issue type
REFACTOR_TEMPLATES: dict[LoopIssueType | MLIssueType, dict[str, str]] = {
    LoopIssueType.NESTED_VECTORIZABLE: {
        "explanation": (
            "Nested loops over arrays can often be replaced with NumPy vectorized "
            "operations. Vectorization leverages optimized C code and SIMD instructions, "
            "dramatically improving performance and reducing energy consumption."
        ),
        "suggestion_template": (
            "# Consider using NumPy vectorization:\n"
            "import numpy as np\n"
            "# Replace nested loops with broadcasting or np.outer/np.dot\n"
            "result = np.outer(arr1, arr2)  # or appropriate vectorized operation"
        ),
    },
    LoopIssueType.REDUNDANT_COMPUTATION: {
        "explanation": (
            "This computation does not depend on the loop variable and is being "
            "recalculated on every iteration. Moving it outside the loop computes "
            "it once, saving CPU cycles and energy."
        ),
        "suggestion_template": (
            "# Move loop-invariant computation outside the loop:\n"
            "precomputed_value = expensive_computation()  # Compute once\n"
            "for item in items:\n"
            "    # Use precomputed_value instead of recomputing"
        ),
    },
    LoopIssueType.UNBATCHED_ITERATION: {
        "explanation": (
            "Processing items one at a time in a loop is inefficient. Batching "
            "operations allows for better memory access patterns, reduced function "
            "call overhead, and potential parallelization."
        ),
        "suggestion_template": (
            "# Consider batching operations:\n"
            "# Instead of:\n"
            "#   for item in items: process(item)\n"
            "# Use:\n"
            "process_batch(items)  # or list comprehension/map"
        ),
    },
    MLIssueType.MODEL_LOADING_IN_LOOP: {
        "explanation": (
            "Loading ML models is extremely expensive (disk I/O, memory allocation, "
            "weight initialization). Loading inside a loop multiplies this cost. "
            "Load the model once before the loop and reuse it."
        ),
        "suggestion_template": (
            "# Load model once outside the loop:\n"
            "model = load_model(model_path)  # Load once\n"
            "for item in items:\n"
            "    result = model.predict(item)  # Reuse loaded model"
        ),
    },
    MLIssueType.UNBATCHED_INFERENCE: {
        "explanation": (
            "Running inference on single items in a loop is inefficient. ML models "
            "are optimized for batch processing, which better utilizes GPU/CPU "
            "parallelism and reduces per-item overhead."
        ),
        "suggestion_template": (
            "# Batch inference calls:\n"
            "# Instead of:\n"
            "#   for item in items: model.predict(item)\n"
            "# Use:\n"
            "batch = np.stack(items)  # or torch.stack\n"
            "results = model.predict(batch)  # Single batched call"
        ),
    },
    MLIssueType.UNUSED_MODEL_OUTPUT: {
        "explanation": (
            "The model output is being discarded. If the output is not needed, "
            "consider removing the call entirely. If only side effects are needed, "
            "document this clearly or use a more efficient approach."
        ),
        "suggestion_template": (
            "# Either use the output:\n"
            "result = model.predict(data)\n"
            "process(result)\n"
            "\n"
            "# Or remove the call if not needed:\n"
            "# model.predict(data)  # Remove if output is unused"
        ),
    },
}


class RefactorPlanner:
    """Generates refactoring suggestions for detected issues.
    
    The RefactorPlanner creates actionable RefactorPlan objects for each
    detected issue, including suggested code transformations and estimated
    savings.
    
    Properties enforced:
    - Property 8: All plans have non-empty required fields
    - Property 14: Generates exactly one plan per issue
    """
    
    def __init__(self) -> None:
        """Initialize the RefactorPlanner."""
        self._templates = REFACTOR_TEMPLATES
        self._time_savings = TIME_SAVINGS
        self._carbon_savings = CARBON_SAVINGS
        self._severity_priority = SEVERITY_PRIORITY
    
    def generate_plan(self, issue: Issue, source_code: str) -> RefactorPlan:
        """Generate a refactoring plan for an issue.
        
        Args:
            issue: The detected issue to generate a plan for
            source_code: The original source code (for context)
            
        Returns:
            A RefactorPlan with suggested improvements
            
        Properties enforced:
            - Property 8: All required fields are non-empty
        """
        template = self._templates.get(issue.issue_type, self._get_default_template())
        
        # Get the original code from the issue
        original_code = issue.code_snippet if issue.code_snippet else self._extract_code(
            source_code, issue.line_number, issue.end_line_number
        )
        
        # Generate suggested code based on the template
        suggested_code = template["suggestion_template"]
        
        # Get explanation
        explanation = template["explanation"]
        
        # Get estimated savings
        time_savings = self._time_savings.get(
            issue.issue_type, "Performance improvement expected"
        )
        carbon_savings = self._carbon_savings.get(
            issue.issue_type, "Carbon reduction expected"
        )
        
        # Calculate priority based on severity
        priority = self._severity_priority.get(issue.severity, 2)
        
        return RefactorPlan(
            issue_id=issue.issue_id,
            original_code=original_code,
            suggested_code=suggested_code,
            explanation=explanation,
            estimated_time_savings=time_savings,
            estimated_carbon_savings=carbon_savings,
            priority=priority,
        )
    
    def generate_plans(self, issues: list[Issue], source_code: str) -> list[RefactorPlan]:
        """Generate refactoring plans for all issues.
        
        Args:
            issues: List of detected issues
            source_code: The original source code
            
        Returns:
            List of RefactorPlans, one per issue
            
        Properties enforced:
            - Property 14: Returns exactly len(issues) plans
        """
        return [self.generate_plan(issue, source_code) for issue in issues]
    
    def prioritize_plans(self, plans: list[RefactorPlan]) -> list[RefactorPlan]:
        """Sort plans by priority (highest priority first).
        
        Args:
            plans: List of refactoring plans to sort
            
        Returns:
            Plans sorted by priority (1 = highest priority comes first)
            
        Properties enforced:
            - Property 9: Plans sorted in ascending order by priority field
        """
        return sorted(plans, key=lambda p: p.priority)
    
    def _get_default_template(self) -> dict[str, str]:
        """Get a default template for unknown issue types.
        
        Returns:
            A default template dictionary
        """
        return {
            "explanation": (
                "This code pattern has been identified as potentially inefficient. "
                "Consider reviewing and optimizing for better performance."
            ),
            "suggestion_template": (
                "# Review this code for optimization opportunities\n"
                "# Consider profiling to identify specific bottlenecks"
            ),
        }
    
    def _extract_code(
        self, source_code: str, start_line: int, end_line: int
    ) -> str:
        """Extract code lines from source.
        
        Args:
            source_code: The full source code
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            
        Returns:
            The extracted code snippet
        """
        lines = source_code.splitlines()
        # Convert to 0-indexed
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        return "\n".join(lines[start_idx:end_idx])
