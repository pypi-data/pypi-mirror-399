"""EcoCode Auditor - Main orchestration class.

This module implements the EcoCodeAuditor class that wires together
all components: FileWatcher, PatternAnalyzer, ScoreCalculator,
RefactorPlanner, and Reporter.

Requirements: 1.1, 6.1, 6.2, 6.3
"""

import hashlib
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from .analysis import PatternAnalyzer
from .models import AnalysisResult, FileEvent
from .refactoring import RefactorPlanner
from .scoring import ScoreCalculator

logger = logging.getLogger(__name__)


class EcoCodeAuditor:
    """Main orchestration class for EcoCode.
    
    Wires together all components to provide file analysis and monitoring
    capabilities. Supports both single-file analysis and directory monitoring.
    
    Attributes:
        analyzer: PatternAnalyzer for detecting code issues
        scorer: ScoreCalculator for computing Green Score
        planner: RefactorPlanner for generating improvement suggestions
    """
    
    def __init__(self) -> None:
        """Initialize the EcoCodeAuditor with all required components."""
        self.analyzer = PatternAnalyzer()
        self.scorer = ScoreCalculator()
        self.planner = RefactorPlanner()
        self._file_watcher: Optional[object] = None
        self._analysis_callback: Optional[Callable[[AnalysisResult], None]] = None
    
    def analyze_file(self, path: Path) -> AnalysisResult:
        """Analyze a Python file for efficiency issues.
        
        This method orchestrates the full analysis pipeline:
        1. Read and hash the source code
        2. Detect issues using PatternAnalyzer
        3. Calculate Green Score using ScoreCalculator
        4. Generate refactor plans using RefactorPlanner
        5. Return complete AnalysisResult
        
        Args:
            path: Path to the Python file to analyze
            
        Returns:
            AnalysisResult containing issues, score, and refactor plans
            
        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
            UnicodeDecodeError: If the file encoding is not supported
            
        Requirements: 6.1, 6.2, 6.3
        """
        start_time = time.perf_counter()
        
        # Read source code
        source_code = self._read_file(path)
        source_hash = hashlib.sha256(source_code.encode("utf-8")).hexdigest()
        
        # Detect issues
        issues = self.analyzer.analyze(source_code, path)
        
        # Calculate Green Score (Requirement 6.1)
        green_score = self.scorer.calculate(issues)
        
        # Generate refactor plans (Requirement 6.2, 6.3)
        plans = self.planner.generate_plans(issues, source_code)
        plans = self.planner.prioritize_plans(plans)
        
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        return AnalysisResult(
            file_path=path,
            source_hash=source_hash,
            green_score=green_score,
            issues=issues,
            refactor_plans=plans,
            analysis_timestamp=datetime.now(),
            analysis_duration_ms=duration_ms,
        )
    
    def start_monitoring(
        self,
        directory: Path,
        callback: Optional[Callable[[AnalysisResult], None]] = None,
    ) -> None:
        """Start monitoring a directory for Python file changes.
        
        When a Python file is saved in the monitored directory, it will
        be automatically analyzed and the callback will be invoked with
        the results.
        
        Args:
            directory: Path to the directory to monitor
            callback: Optional callback to invoke with analysis results
            
        Raises:
            NotImplementedError: If FileWatcher is not available
            FileNotFoundError: If the directory does not exist
            
        Requirements: 1.1
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        self._analysis_callback = callback
        
        # Try to import and use FileWatcher if available
        try:
            from .watcher import FileWatcher
            
            self._file_watcher = FileWatcher()
            self._file_watcher.on_file_saved(self._on_file_event)
            self._file_watcher.start(directory)
            logger.info(f"Started monitoring directory: {directory}")
        except ImportError:
            raise NotImplementedError(
                "FileWatcher is not yet implemented. "
                "Use analyze_file() for single file analysis."
            )
    
    def stop_monitoring(self) -> None:
        """Stop monitoring the directory.
        
        Cleans up resources and stops the file watcher.
        """
        if self._file_watcher is not None:
            self._file_watcher.stop()
            self._file_watcher = None
            logger.info("Stopped monitoring")
    
    def _on_file_event(self, event: FileEvent) -> None:
        """Handle a file event from the FileWatcher.
        
        Args:
            event: The file event that occurred
        """
        if not self._is_python_file(event.path):
            return
        
        try:
            result = self.analyze_file(event.path)
            if self._analysis_callback:
                self._analysis_callback(result)
        except Exception as e:
            logger.error(f"Error analyzing file {event.path}: {e}")
    
    def _is_python_file(self, path: Path) -> bool:
        """Check if a file is a Python file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the file has a .py extension
        """
        return path.suffix.lower() == ".py"
    
    def _read_file(self, path: Path) -> str:
        """Read a file with error handling.
        
        Attempts UTF-8 encoding first, falls back to latin-1.
        
        Args:
            path: Path to the file to read
            
        Returns:
            The file contents as a string
            
        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
        """
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {path}, trying latin-1")
            return path.read_text(encoding="latin-1")
