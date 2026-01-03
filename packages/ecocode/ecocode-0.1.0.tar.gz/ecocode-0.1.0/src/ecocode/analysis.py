"""Pattern analysis for EcoCode.

This module implements the PatternAnalyzer and pattern detectors for
detecting inefficient code patterns in Python source files.

Properties enforced:
- Property 2: All issues have required fields (line_number > 0, non-empty issue_type, valid severity)
- Property 11: Nested array loops are detected
"""

import ast
import uuid
from pathlib import Path
from typing import Protocol

from .models import Issue, IssueCategory, LoopIssueType, MLIssueType, Severity


class PatternDetector(Protocol):
    """Protocol for pattern detectors.
    
    Pattern detectors analyze an AST tree and return detected issues.
    """
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        ...
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect specific patterns in the AST.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected issues
        """
        ...


class UnbatchedIterationDetector:
    """Detects single-item processing in loops that could be batched.
    
    This detector finds loops that process items one at a time when they
    could potentially be batched for better performance.
    
    Patterns detected:
    - Loops calling functions on individual items that could accept batches
    - Loops appending to lists that could use list comprehensions
    - Loops with database/API calls that could be batched
    
    Ignores string-building patterns (loops that primarily append strings).
    """
    
    # Common functions that often have batch equivalents
    BATCHABLE_FUNCTIONS = {
        'append', 'insert', 'write', 'send', 'post', 'get',
        'execute', 'query', 'fetch', 'save', 'update', 'delete',
        'process', 'transform', 'convert', 'encode', 'decode',
    }
    
    # Methods that are typically used for string building (not batchable concerns)
    STRING_BUILDING_METHODS = {'append'}
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.INEFFICIENT_LOOP
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect unbatched iteration patterns.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected unbatched iteration issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.For):
                # Skip string-building loops
                if self._is_string_building_loop(node):
                    continue
                loop_issues = self._analyze_loop(node, source_lines)
                issues.extend(loop_issues)
        
        return issues
    
    def _is_string_building_loop(self, loop: ast.For) -> bool:
        """Check if a loop is primarily used for string building/formatting.
        
        Args:
            loop: The for-loop AST node
            
        Returns:
            True if this appears to be a string-building loop
        """
        # Check if iterating over a string split
        if isinstance(loop.iter, ast.Subscript):
            if isinstance(loop.iter.value, ast.Call):
                call = loop.iter.value
                if isinstance(call.func, ast.Attribute):
                    if call.func.attr in ('split', 'splitlines'):
                        return True
        
        if isinstance(loop.iter, ast.Call):
            call = loop.iter
            if isinstance(call.func, ast.Attribute):
                if call.func.attr in ('split', 'splitlines'):
                    return True
        
        # Check if the loop body is primarily string appends
        string_append_count = 0
        total_statements = 0
        
        for stmt in loop.body:
            total_statements += 1
            if self._is_string_append(stmt):
                string_append_count += 1
            # Also count conditionals that contain string appends
            elif isinstance(stmt, ast.If):
                for inner_stmt in stmt.body + stmt.orelse:
                    if self._is_string_append(inner_stmt):
                        string_append_count += 0.5  # Partial credit for conditional appends
        
        # If most statements are string appends, it's a string-building loop
        if total_statements > 0 and string_append_count / total_statements >= 0.4:
            return True
        
        return False
    
    def _is_string_append(self, stmt: ast.stmt) -> bool:
        """Check if a statement is a string append operation.
        
        Args:
            stmt: The statement to check
            
        Returns:
            True if this is a string append (e.g., lines.append(f"..."))
        """
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Attribute):
                if call.func.attr == 'append' and call.args:
                    arg = call.args[0]
                    # Check if appending a string or f-string
                    if isinstance(arg, (ast.Constant, ast.JoinedStr)):
                        if isinstance(arg, ast.Constant):
                            return isinstance(arg.value, str)
                        return True  # JoinedStr is an f-string
        return False
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.INEFFICIENT_LOOP
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect unbatched iteration patterns.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected unbatched iteration issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.For):
                loop_issues = self._analyze_loop(node, source_lines)
                issues.extend(loop_issues)
        
        return issues
    
    def _analyze_loop(self, loop: ast.For, source_lines: list[str]) -> list[Issue]:
        """Analyze a for-loop for unbatched iteration patterns.
        
        Args:
            loop: The for-loop AST node
            source_lines: Source code lines
            
        Returns:
            List of issues found in this loop
        """
        issues: list[Issue] = []
        loop_vars = self._get_loop_variables(loop.target)
        
        # Look for patterns in the loop body
        for stmt in loop.body:
            # Pattern 1: list.append(item) in a loop
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if self._is_batchable_method_call(call, loop_vars):
                    issue = self._create_issue(stmt, loop, source_lines, "method call")
                    issues.append(issue)
            
            # Pattern 2: Single function call with loop variable
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if self._is_single_item_function_call(call, loop_vars):
                    issue = self._create_issue(stmt, loop, source_lines, "function call")
                    issues.append(issue)
        
        return issues
    
    def _get_loop_variables(self, target: ast.AST) -> set[str]:
        """Extract variable names from a loop target."""
        names: set[str] = set()
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                names.update(self._get_loop_variables(elt))
        return names
    
    def _is_batchable_method_call(self, call: ast.Call, loop_vars: set[str]) -> bool:
        """Check if a call is a batchable method call using loop variable.
        
        Args:
            call: The function call AST node
            loop_vars: Set of loop variable names
            
        Returns:
            True if this is a batchable method call
        """
        # Check for method calls like obj.append(item)
        if isinstance(call.func, ast.Attribute):
            method_name = call.func.attr.lower()
            if method_name in self.BATCHABLE_FUNCTIONS:
                # Check if any argument uses the loop variable
                for arg in call.args:
                    if self._uses_loop_var(arg, loop_vars):
                        return True
        return False
    
    def _is_single_item_function_call(self, call: ast.Call, loop_vars: set[str]) -> bool:
        """Check if a call processes a single item from the loop.
        
        Args:
            call: The function call AST node
            loop_vars: Set of loop variable names
            
        Returns:
            True if this is a single-item processing call
        """
        # Check for function calls like process(item)
        if isinstance(call.func, ast.Name):
            func_name = call.func.id.lower()
            if func_name in self.BATCHABLE_FUNCTIONS:
                for arg in call.args:
                    if self._uses_loop_var(arg, loop_vars):
                        return True
        return False
    
    def _uses_loop_var(self, node: ast.AST, loop_vars: set[str]) -> bool:
        """Check if an AST node uses any loop variable.
        
        Args:
            node: The AST node to check
            loop_vars: Set of loop variable names
            
        Returns:
            True if the node references a loop variable
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id in loop_vars:
                return True
        return False
    
    def _create_issue(
        self,
        stmt: ast.stmt,
        loop: ast.For,
        source_lines: list[str],
        pattern_type: str
    ) -> Issue:
        """Create an Issue for a detected unbatched iteration.
        
        Args:
            stmt: The statement with unbatched processing
            loop: The containing for-loop
            source_lines: Source code lines
            pattern_type: Type of pattern detected
            
        Returns:
            A properly structured Issue
        """
        start_line = loop.lineno
        end_line = loop.end_lineno or loop.lineno
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.INEFFICIENT_LOOP,
            issue_type=LoopIssueType.UNBATCHED_ITERATION,
            line_number=stmt.lineno,
            column=stmt.col_offset,
            end_line_number=stmt.end_lineno or stmt.lineno,
            end_column=stmt.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.MEDIUM,
            description=(
                f"Unbatched {pattern_type} detected at line {stmt.lineno}. "
                "Consider batching operations for better performance."
            ),
            metadata={
                "loop_line": loop.lineno,
                "pattern_type": pattern_type,
            },
        )


class RedundantComputationDetector:
    """Detects loop-invariant expressions that could be moved outside the loop.
    
    This detector finds expressions inside loops that don't depend on the loop
    variable, indicating they could be computed once before the loop.
    
    Property 12: Redundant Computation Detection - Loop-invariant code detected
    """
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.INEFFICIENT_LOOP
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect redundant computations inside loops.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected redundant computation issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        # Find all for-loops and analyze their bodies
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.For):
                loop_issues = self._analyze_loop(node, source_lines)
                issues.extend(loop_issues)
        
        return issues
    
    def _analyze_loop(self, loop: ast.For, source_lines: list[str]) -> list[Issue]:
        """Analyze a for-loop for redundant computations.
        
        Args:
            loop: The for-loop AST node
            source_lines: Source code lines
            
        Returns:
            List of issues found in this loop
        """
        issues: list[Issue] = []
        
        # Get the loop variable(s)
        loop_vars = self._get_loop_variables(loop.target)
        
        # Analyze assignments in the loop body
        for stmt in loop.body:
            if isinstance(stmt, ast.Assign):
                # Check if the right-hand side is loop-invariant
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        assigned_var = target.id
                        # Skip if the assigned variable is used in the RHS
                        # (this would be an accumulator pattern)
                        rhs_vars = self._get_referenced_names(stmt.value)
                        if assigned_var not in rhs_vars:
                            if self._is_loop_invariant(stmt.value, loop_vars):
                                issue = self._create_issue(stmt, loop, source_lines)
                                issues.append(issue)
        
        return issues
    
    def _get_loop_variables(self, target: ast.AST) -> set[str]:
        """Extract variable names from a loop target.
        
        Handles simple names and tuple unpacking.
        
        Args:
            target: The loop target AST node
            
        Returns:
            Set of variable names used as loop variables
        """
        names: set[str] = set()
        
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                names.update(self._get_loop_variables(elt))
        
        return names
    
    def _get_referenced_names(self, node: ast.AST) -> set[str]:
        """Get all variable names referenced in an expression.
        
        Args:
            node: The AST node to analyze
            
        Returns:
            Set of variable names referenced
        """
        names: set[str] = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.add(child.id)
        
        return names
    
    def _is_loop_invariant(self, expr: ast.AST, loop_vars: set[str]) -> bool:
        """Check if an expression is loop-invariant.
        
        An expression is loop-invariant if it doesn't reference any loop variables.
        We also check for function calls that might have side effects or depend
        on external state.
        
        Args:
            expr: The expression AST node
            loop_vars: Set of loop variable names
            
        Returns:
            True if the expression is loop-invariant
        """
        # Get all names referenced in the expression
        referenced_names = self._get_referenced_names(expr)
        
        # If any loop variable is referenced, it's not loop-invariant
        if referenced_names & loop_vars:
            return False
        
        # Check if there's a non-trivial computation (not just a simple name or constant)
        # We want to flag computations that could be expensive
        has_computation = False
        for child in ast.walk(expr):
            if isinstance(child, (ast.Call, ast.BinOp, ast.UnaryOp, ast.Compare)):
                has_computation = True
                break
        
        return has_computation
    
    def _create_issue(
        self,
        stmt: ast.Assign,
        loop: ast.For,
        source_lines: list[str]
    ) -> Issue:
        """Create an Issue for a detected redundant computation.
        
        Args:
            stmt: The assignment statement with redundant computation
            loop: The containing for-loop
            source_lines: Source code lines
            
        Returns:
            A properly structured Issue
        """
        # Get the code snippet for the assignment
        start_line = stmt.lineno
        end_line = stmt.end_lineno or stmt.lineno
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.INEFFICIENT_LOOP,
            issue_type=LoopIssueType.REDUNDANT_COMPUTATION,
            line_number=stmt.lineno,
            column=stmt.col_offset,
            end_line_number=stmt.end_lineno or stmt.lineno,
            end_column=stmt.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.MEDIUM,
            description=(
                f"Loop-invariant computation detected at line {stmt.lineno}. "
                "This expression does not depend on the loop variable and could "
                "be moved outside the loop for better performance."
            ),
            metadata={
                "loop_line": loop.lineno,
                "computation_line": stmt.lineno,
            },
        )


class NestedLoopDetector:
    """Detects nested for-loops that could potentially be vectorized.
    
    This detector finds for-loops nested inside other for-loops,
    which often indicate opportunities for vectorization using
    NumPy or similar libraries.
    
    Ignores string-building patterns (loops that primarily append strings).
    """
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.INEFFICIENT_LOOP
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect nested for-loops in the AST.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected nested loop issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        reported_pairs: set[tuple[int, int]] = set()
        
        # Find all nested for-loops using a visitor pattern
        self._find_nested_loops_recursive(ast_tree, [], issues, source_lines, reported_pairs)
        
        return issues
    
    def _is_string_building_loop(self, loop: ast.For) -> bool:
        """Check if a loop is primarily used for string building/formatting.
        
        String-building loops typically:
        - Iterate over strings or string splits
        - Append formatted strings to a list
        - Build output for display/logging
        
        Args:
            loop: The for-loop AST node
            
        Returns:
            True if this appears to be a string-building loop
        """
        # Check if iterating over a string split (common pattern)
        if isinstance(loop.iter, ast.Subscript):
            # Pattern: something.split('\n')[:5]
            if isinstance(loop.iter.value, ast.Call):
                call = loop.iter.value
                if isinstance(call.func, ast.Attribute):
                    if call.func.attr == 'split':
                        return True
        
        if isinstance(loop.iter, ast.Call):
            call = loop.iter
            if isinstance(call.func, ast.Attribute):
                # Pattern: something.split('\n')
                if call.func.attr in ('split', 'splitlines'):
                    return True
        
        # Check if the loop body is primarily string appends
        string_append_count = 0
        total_statements = len(loop.body)
        
        for stmt in loop.body:
            if self._is_string_append(stmt):
                string_append_count += 1
        
        # If most statements are string appends, it's a string-building loop
        if total_statements > 0 and string_append_count / total_statements >= 0.5:
            return True
        
        return False
    
    def _is_string_append(self, stmt: ast.stmt) -> bool:
        """Check if a statement is a string append operation.
        
        Args:
            stmt: The statement to check
            
        Returns:
            True if this is a string append (e.g., lines.append(f"..."))
        """
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Attribute):
                if call.func.attr == 'append' and call.args:
                    arg = call.args[0]
                    # Check if appending a string or f-string
                    if isinstance(arg, (ast.Constant, ast.JoinedStr)):
                        if isinstance(arg, ast.Constant):
                            return isinstance(arg.value, str)
                        return True  # JoinedStr is an f-string
        return False
    
    def _find_nested_loops_recursive(
        self,
        node: ast.AST,
        parent_loops: list[ast.For],
        issues: list[Issue],
        source_lines: list[str],
        reported_pairs: set[tuple[int, int]],
    ) -> None:
        """Recursively find nested for-loops.
        
        Args:
            node: Current AST node
            parent_loops: Stack of parent for-loops
            issues: List to append detected issues to
            source_lines: Source code lines
            reported_pairs: Set of (outer_line, inner_line) already reported
        """
        if isinstance(node, ast.For):
            # If we have a parent loop, this is a nested loop
            if parent_loops:
                outer_loop = parent_loops[-1]  # Immediate parent
                pair = (outer_loop.lineno, node.lineno)
                # Skip if already reported or if this is a string-building loop
                if pair not in reported_pairs and not self._is_string_building_loop(node):
                    reported_pairs.add(pair)
                    issue = self._create_issue(outer_loop, node, source_lines)
                    issues.append(issue)
            
            # Add this loop to the stack and recurse into its body
            new_parent_loops = parent_loops + [node]
            for child in ast.iter_child_nodes(node):
                self._find_nested_loops_recursive(
                    child, new_parent_loops, issues, source_lines, reported_pairs
                )
        else:
            # Not a for-loop, just recurse into children
            for child in ast.iter_child_nodes(node):
                self._find_nested_loops_recursive(
                    child, parent_loops, issues, source_lines, reported_pairs
                )
    
    def _create_issue(
        self, 
        outer_loop: ast.For, 
        inner_loop: ast.For, 
        source_lines: list[str]
    ) -> Issue:
        """Create an Issue for a detected nested loop.
        
        Ensures Property 2: Issue Structure Completeness
        - line_number > 0
        - non-empty issue_type
        - valid severity
        
        Args:
            outer_loop: The outer for-loop AST node
            inner_loop: The inner for-loop AST node
            source_lines: The source code split into lines
            
        Returns:
            A properly structured Issue
        """
        # Extract code snippet for the nested loop region
        start_line = outer_loop.lineno
        end_line = inner_loop.end_lineno or inner_loop.lineno
        
        # Get the code snippet (1-indexed to 0-indexed conversion)
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.INEFFICIENT_LOOP,
            issue_type=LoopIssueType.NESTED_VECTORIZABLE,
            line_number=inner_loop.lineno,  # Property 2: line_number > 0
            column=inner_loop.col_offset,
            end_line_number=inner_loop.end_lineno or inner_loop.lineno,
            end_column=inner_loop.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.HIGH,  # Property 2: valid severity
            description=(
                f"Nested for-loop detected at line {inner_loop.lineno}. "
                "Consider using NumPy vectorization or list comprehensions "
                "for better performance."
            ),
            metadata={
                "outer_loop_line": outer_loop.lineno,
                "inner_loop_line": inner_loop.lineno,
                "nesting_depth": self._get_nesting_depth(outer_loop, inner_loop),
            },
        )
    
    def _get_nesting_depth(self, outer_loop: ast.For, inner_loop: ast.For) -> int:
        """Calculate the nesting depth between outer and inner loops.
        
        Args:
            outer_loop: The outer for-loop
            inner_loop: The inner for-loop
            
        Returns:
            The nesting depth (1 = directly nested)
        """
        depth = 0
        for node in ast.walk(outer_loop):
            if isinstance(node, ast.For):
                depth += 1
                if node is inner_loop:
                    return depth - 1  # Subtract 1 for the outer loop itself
        return 1


class ModelLoadingDetector:
    """Detects model loading calls inside loops.
    
    This detector finds ML model loading operations (torch.load, 
    tf.keras.models.load_model, joblib.load, etc.) that occur inside loops,
    which is highly inefficient as models should be loaded once.
    
    Property 13: Model Loading in Loop Detection - Model loads in loops detected
    Requirements: 3.1
    """
    
    # Model loading function patterns to detect
    MODEL_LOAD_PATTERNS = {
        # PyTorch
        ('torch', 'load'),
        # TensorFlow/Keras
        ('tf', 'keras', 'models', 'load_model'),
        ('keras', 'models', 'load_model'),
        ('tensorflow', 'keras', 'models', 'load_model'),
        # Joblib
        ('joblib', 'load'),
        # Pickle (common for sklearn models)
        ('pickle', 'load'),
        # Transformers
        ('transformers', 'AutoModel', 'from_pretrained'),
        ('transformers', 'AutoTokenizer', 'from_pretrained'),
    }
    
    # Simple function names that indicate model loading
    LOAD_FUNCTION_NAMES = {
        'load_model', 'load_weights', 'from_pretrained',
    }
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.HEAVY_ML_CALL
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect model loading calls inside loops.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected model loading in loop issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        # Find all loops and check for model loading calls inside them
        self._find_model_loads_in_loops(ast_tree, [], issues, source_lines)
        
        return issues
    
    def _find_model_loads_in_loops(
        self,
        node: ast.AST,
        parent_loops: list[ast.For | ast.While],
        issues: list[Issue],
        source_lines: list[str],
    ) -> None:
        """Recursively find model loading calls inside loops.
        
        Args:
            node: Current AST node
            parent_loops: Stack of parent loops
            issues: List to append detected issues to
            source_lines: Source code lines
        """
        if isinstance(node, (ast.For, ast.While)):
            # Add this loop to the stack and recurse
            new_parent_loops = parent_loops + [node]
            for child in ast.iter_child_nodes(node):
                self._find_model_loads_in_loops(child, new_parent_loops, issues, source_lines)
        elif isinstance(node, ast.Call):
            # Check if this is a model loading call inside a loop
            if parent_loops and self._is_model_load_call(node):
                issue = self._create_issue(node, parent_loops[-1], source_lines)
                issues.append(issue)
            # Still recurse into the call's children
            for child in ast.iter_child_nodes(node):
                self._find_model_loads_in_loops(child, parent_loops, issues, source_lines)
        else:
            # Recurse into children
            for child in ast.iter_child_nodes(node):
                self._find_model_loads_in_loops(child, parent_loops, issues, source_lines)
    
    def _is_model_load_call(self, call: ast.Call) -> bool:
        """Check if a call is a model loading operation.
        
        Args:
            call: The function call AST node
            
        Returns:
            True if this is a model loading call
        """
        # Get the full attribute chain
        attr_chain = self._get_attribute_chain(call.func)
        
        if not attr_chain:
            return False
        
        # Check against known patterns
        for pattern in self.MODEL_LOAD_PATTERNS:
            if self._matches_pattern(attr_chain, pattern):
                return True
        
        # Check if the last part of the chain is a known load function
        if attr_chain[-1] in self.LOAD_FUNCTION_NAMES:
            return True
        
        return False
    
    def _get_attribute_chain(self, node: ast.AST) -> list[str]:
        """Get the chain of attributes from a node.
        
        For example, torch.load becomes ['torch', 'load']
        
        Args:
            node: The AST node
            
        Returns:
            List of attribute names in order
        """
        chain: list[str] = []
        
        while isinstance(node, ast.Attribute):
            chain.insert(0, node.attr)
            node = node.value
        
        if isinstance(node, ast.Name):
            chain.insert(0, node.id)
        
        return chain
    
    def _matches_pattern(self, chain: list[str], pattern: tuple[str, ...]) -> bool:
        """Check if an attribute chain matches a pattern.
        
        Args:
            chain: The attribute chain from the code
            pattern: The pattern to match against
            
        Returns:
            True if the chain ends with the pattern
        """
        if len(chain) < len(pattern):
            return False
        
        # Check if the chain ends with the pattern
        return tuple(chain[-len(pattern):]) == pattern
    
    def _create_issue(
        self,
        call: ast.Call,
        loop: ast.For | ast.While,
        source_lines: list[str],
    ) -> Issue:
        """Create an Issue for a detected model loading in loop.
        
        Args:
            call: The model loading call AST node
            loop: The containing loop
            source_lines: Source code lines
            
        Returns:
            A properly structured Issue
        """
        # Get the code snippet for the call
        start_line = call.lineno
        end_line = call.end_lineno or call.lineno
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        # Get the function name for the description
        func_name = self._get_function_name(call.func)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.HEAVY_ML_CALL,
            issue_type=MLIssueType.MODEL_LOADING_IN_LOOP,
            line_number=call.lineno,
            column=call.col_offset,
            end_line_number=call.end_lineno or call.lineno,
            end_column=call.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.HIGH,
            description=(
                f"Model loading call '{func_name}' detected inside loop at line {call.lineno}. "
                "Loading models is expensive and should be done once outside the loop."
            ),
            metadata={
                "loop_line": loop.lineno,
                "function_name": func_name,
            },
        )
    
    def _get_function_name(self, func: ast.AST) -> str:
        """Get a readable function name from a call's func attribute.
        
        Args:
            func: The func attribute of an ast.Call
            
        Returns:
            A readable function name string
        """
        chain = self._get_attribute_chain(func)
        return ".".join(chain) if chain else "unknown"


class UnbatchedInferenceDetector:
    """Detects single-item inference calls inside loops.
    
    This detector finds ML model inference operations (model.predict(),
    model.forward(), model()) that occur inside loops without batching,
    which is inefficient as inference should be batched.
    
    Requirements: 3.2
    """
    
    # Inference method names to detect
    INFERENCE_METHODS = {
        'predict', 'predict_proba', 'predict_log_proba',
        'forward', '__call__', 'infer', 'inference',
        'generate', 'encode', 'decode',
    }
    
    # Common model variable name patterns
    MODEL_NAME_PATTERNS = {
        'model', 'classifier', 'regressor', 'estimator',
        'net', 'network', 'nn', 'transformer', 'bert',
        'gpt', 'llm', 'encoder', 'decoder', 'predictor',
    }
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.HEAVY_ML_CALL
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect unbatched inference calls inside loops.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected unbatched inference issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        # Find all loops and check for inference calls inside them
        self._find_inference_in_loops(ast_tree, [], issues, source_lines)
        
        return issues
    
    def _find_inference_in_loops(
        self,
        node: ast.AST,
        parent_loops: list[ast.For | ast.While],
        issues: list[Issue],
        source_lines: list[str],
    ) -> None:
        """Recursively find inference calls inside loops.
        
        Args:
            node: Current AST node
            parent_loops: Stack of parent loops
            issues: List to append detected issues to
            source_lines: Source code lines
        """
        if isinstance(node, (ast.For, ast.While)):
            # Add this loop to the stack and recurse
            new_parent_loops = parent_loops + [node]
            for child in ast.iter_child_nodes(node):
                self._find_inference_in_loops(child, new_parent_loops, issues, source_lines)
        elif isinstance(node, ast.Call):
            # Check if this is an inference call inside a loop
            if parent_loops and self._is_inference_call(node):
                issue = self._create_issue(node, parent_loops[-1], source_lines)
                issues.append(issue)
            # Still recurse into the call's children
            for child in ast.iter_child_nodes(node):
                self._find_inference_in_loops(child, parent_loops, issues, source_lines)
        else:
            # Recurse into children
            for child in ast.iter_child_nodes(node):
                self._find_inference_in_loops(child, parent_loops, issues, source_lines)
    
    def _is_inference_call(self, call: ast.Call) -> bool:
        """Check if a call is a model inference operation.
        
        Args:
            call: The function call AST node
            
        Returns:
            True if this is an inference call
        """
        # Pattern 1: model.predict(x), model.forward(x), etc.
        if isinstance(call.func, ast.Attribute):
            method_name = call.func.attr.lower()
            if method_name in self.INFERENCE_METHODS:
                # Check if the object looks like a model
                obj_name = self._get_object_name(call.func.value)
                if obj_name and self._looks_like_model(obj_name):
                    return True
        
        # Pattern 2: model(x) - direct call on model object
        if isinstance(call.func, ast.Name):
            name = call.func.id.lower()
            if self._looks_like_model(name):
                return True
        
        return False
    
    def _get_object_name(self, node: ast.AST) -> str | None:
        """Get the name of an object from an AST node.
        
        Args:
            node: The AST node
            
        Returns:
            The object name or None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _looks_like_model(self, name: str) -> bool:
        """Check if a name looks like a model variable.
        
        Args:
            name: The variable name
            
        Returns:
            True if the name suggests it's a model
        """
        name_lower = name.lower()
        for pattern in self.MODEL_NAME_PATTERNS:
            if pattern in name_lower:
                return True
        return False
    
    def _create_issue(
        self,
        call: ast.Call,
        loop: ast.For | ast.While,
        source_lines: list[str],
    ) -> Issue:
        """Create an Issue for a detected unbatched inference.
        
        Args:
            call: The inference call AST node
            loop: The containing loop
            source_lines: Source code lines
            
        Returns:
            A properly structured Issue
        """
        # Get the code snippet for the call
        start_line = call.lineno
        end_line = call.end_lineno or call.lineno
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        # Get the function name for the description
        func_name = self._get_function_name(call.func)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.HEAVY_ML_CALL,
            issue_type=MLIssueType.UNBATCHED_INFERENCE,
            line_number=call.lineno,
            column=call.col_offset,
            end_line_number=call.end_lineno or call.lineno,
            end_column=call.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.HIGH,
            description=(
                f"Unbatched inference call '{func_name}' detected inside loop at line {call.lineno}. "
                "Consider batching inputs for more efficient inference."
            ),
            metadata={
                "loop_line": loop.lineno,
                "function_name": func_name,
            },
        )
    
    def _get_function_name(self, func: ast.AST) -> str:
        """Get a readable function name from a call's func attribute.
        
        Args:
            func: The func attribute of an ast.Call
            
        Returns:
            A readable function name string
        """
        if isinstance(func, ast.Attribute):
            obj_name = self._get_object_name(func.value)
            return f"{obj_name}.{func.attr}" if obj_name else func.attr
        elif isinstance(func, ast.Name):
            return func.id
        return "unknown"


class UnusedOutputDetector:
    """Detects model calls where the return value is not used.
    
    This detector finds ML model inference operations where the output
    is discarded, which wastes computation.
    
    Requirements: 3.3
    """
    
    # Inference method names that produce outputs
    OUTPUT_PRODUCING_METHODS = {
        'predict', 'predict_proba', 'predict_log_proba',
        'forward', 'infer', 'inference',
        'generate', 'encode', 'decode',
        'transform', 'fit_transform',
    }
    
    # Common model variable name patterns
    MODEL_NAME_PATTERNS = {
        'model', 'classifier', 'regressor', 'estimator',
        'net', 'network', 'nn', 'transformer', 'bert',
        'gpt', 'llm', 'encoder', 'decoder', 'predictor',
    }
    
    @property
    def category(self) -> IssueCategory:
        """Return the category of issues this detector finds."""
        return IssueCategory.HEAVY_ML_CALL
    
    def detect(self, ast_tree: ast.AST, source_code: str) -> list[Issue]:
        """Detect unused model outputs.
        
        Args:
            ast_tree: The parsed AST of the source code
            source_code: The original source code string
            
        Returns:
            List of detected unused output issues
        """
        issues: list[Issue] = []
        source_lines = source_code.splitlines()
        
        # Walk the AST looking for expression statements with model calls
        for node in ast.walk(ast_tree):
            # Expression statements are calls whose return value is discarded
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if self._is_output_producing_call(call):
                    issue = self._create_issue(call, source_lines)
                    issues.append(issue)
        
        return issues
    
    def _is_output_producing_call(self, call: ast.Call) -> bool:
        """Check if a call produces an output that should be used.
        
        Args:
            call: The function call AST node
            
        Returns:
            True if this is an output-producing model call
        """
        # Pattern: model.predict(x), model.forward(x), etc.
        if isinstance(call.func, ast.Attribute):
            method_name = call.func.attr.lower()
            if method_name in self.OUTPUT_PRODUCING_METHODS:
                # Check if the object looks like a model
                obj_name = self._get_object_name(call.func.value)
                if obj_name and self._looks_like_model(obj_name):
                    return True
        
        return False
    
    def _get_object_name(self, node: ast.AST) -> str | None:
        """Get the name of an object from an AST node.
        
        Args:
            node: The AST node
            
        Returns:
            The object name or None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _looks_like_model(self, name: str) -> bool:
        """Check if a name looks like a model variable.
        
        Args:
            name: The variable name
            
        Returns:
            True if the name suggests it's a model
        """
        name_lower = name.lower()
        for pattern in self.MODEL_NAME_PATTERNS:
            if pattern in name_lower:
                return True
        return False
    
    def _create_issue(
        self,
        call: ast.Call,
        source_lines: list[str],
    ) -> Issue:
        """Create an Issue for a detected unused output.
        
        Args:
            call: The model call AST node
            source_lines: Source code lines
            
        Returns:
            A properly structured Issue
        """
        # Get the code snippet for the call
        start_line = call.lineno
        end_line = call.end_lineno or call.lineno
        snippet_lines = source_lines[start_line - 1:end_line]
        code_snippet = "\n".join(snippet_lines)
        
        # Get the function name for the description
        func_name = self._get_function_name(call.func)
        
        return Issue(
            issue_id=str(uuid.uuid4()),
            category=IssueCategory.HEAVY_ML_CALL,
            issue_type=MLIssueType.UNUSED_MODEL_OUTPUT,
            line_number=call.lineno,
            column=call.col_offset,
            end_line_number=call.end_lineno or call.lineno,
            end_column=call.end_col_offset or 0,
            code_snippet=code_snippet,
            severity=Severity.MEDIUM,
            description=(
                f"Unused model output from '{func_name}' at line {call.lineno}. "
                "The return value is discarded, wasting computation."
            ),
            metadata={
                "function_name": func_name,
            },
        )
    
    def _get_function_name(self, func: ast.AST) -> str:
        """Get a readable function name from a call's func attribute.
        
        Args:
            func: The func attribute of an ast.Call
            
        Returns:
            A readable function name string
        """
        if isinstance(func, ast.Attribute):
            obj_name = self._get_object_name(func.value)
            return f"{obj_name}.{func.attr}" if obj_name else func.attr
        elif isinstance(func, ast.Name):
            return func.id
        return "unknown"


def get_ignored_lines(source_code: str) -> set[int]:
    """Extract line numbers that have '# ecocode: ignore' comments.
    
    Supports both inline comments and comments on the preceding line.
    
    Args:
        source_code: The source code to scan
        
    Returns:
        Set of line numbers (1-indexed) that should be ignored
    """
    ignored_lines: set[int] = set()
    lines = source_code.splitlines()
    
    for i, line in enumerate(lines):
        line_num = i + 1  # 1-indexed
        # Check for inline comment or standalone comment
        if "# ecocode: ignore" in line.lower() or "#ecocode: ignore" in line.lower():
            # This line should be ignored
            ignored_lines.add(line_num)
            # If this is a standalone comment, also ignore the next line
            stripped = line.strip()
            if stripped.startswith("#"):
                ignored_lines.add(line_num + 1)
    
    return ignored_lines


class PatternAnalyzer:
    """Analyzes Python source code to detect inefficient patterns.
    
    Uses AST traversal and registered pattern detectors to find
    issues in the code.
    
    Supports exclusion comments: lines with '# ecocode: ignore' are skipped.
    """
    
    def __init__(self) -> None:
        """Initialize the PatternAnalyzer with default detectors."""
        self._detectors: list[PatternDetector] = []
        
        # Register default loop detectors
        self.register_detector(NestedLoopDetector())
        self.register_detector(RedundantComputationDetector())
        self.register_detector(UnbatchedIterationDetector())
        
        # Register ML pattern detectors
        self.register_detector(ModelLoadingDetector())
        self.register_detector(UnbatchedInferenceDetector())
        self.register_detector(UnusedOutputDetector())
    
    def register_detector(self, detector: PatternDetector) -> None:
        """Register a new pattern detector.
        
        Args:
            detector: The pattern detector to register
        """
        self._detectors.append(detector)
    
    def analyze(self, source_code: str, file_path: Path) -> list[Issue]:
        """Analyze source code and return detected issues.
        
        Args:
            source_code: The Python source code to analyze
            file_path: Path to the source file (for error reporting)
            
        Returns:
            List of detected issues from all registered detectors
        """
        try:
            ast_tree = ast.parse(source_code)
        except SyntaxError:
            # Return empty list for files with syntax errors
            # as per design: "Return empty issue list, log parse error"
            return []
        
        # Get lines to ignore based on '# ecocode: ignore' comments
        ignored_lines = get_ignored_lines(source_code)
        
        issues: list[Issue] = []
        
        for detector in self._detectors:
            try:
                detected = detector.detect(ast_tree, source_code)
                # Filter out issues on ignored lines
                for issue in detected:
                    if issue.line_number not in ignored_lines:
                        issues.append(issue)
            except Exception:
                # Continue with other detectors if one fails
                # as per design: "Catch exception, log error, continue"
                continue
        
        return issues
