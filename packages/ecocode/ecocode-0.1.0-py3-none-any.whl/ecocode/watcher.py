"""FileWatcher - File system monitoring for EcoCode.

This module implements the FileWatcher class that monitors directories
for Python file changes using the watchdog library.

Requirements: 1.1, 1.2, 1.3, 1.4
"""

import logging
import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .models import FileEvent

logger = logging.getLogger(__name__)


class PythonFileHandler(FileSystemEventHandler):
    """Event handler that filters for Python files only.
    
    This handler processes file system events and only triggers
    callbacks for .py files, ignoring all other file types.
    
    Requirements: 1.1, 1.2
    """
    
    def __init__(
        self,
        callback: Callable[[FileEvent], None],
        analysis_queue: "queue.Queue[FileEvent]",
    ) -> None:
        """Initialize the handler.
        
        Args:
            callback: Function to call when a Python file is saved
            analysis_queue: Queue to add pending file events
        """
        super().__init__()
        self._callback = callback
        self._analysis_queue = analysis_queue
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.
        
        Args:
            event: The file system event
        """
        self._handle_event(event, "modified")
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.
        
        Args:
            event: The file system event
        """
        self._handle_event(event, "created")
    
    def _handle_event(self, event: FileSystemEvent, event_type: str) -> None:
        """Process a file system event.
        
        Only processes events for Python files (.py extension).
        Non-Python files are ignored per Requirement 1.2.
        
        Args:
            event: The file system event
            event_type: Type of event ("modified", "created")
        """
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # Requirement 1.2: Ignore non-Python files
        if not is_python_file(path):
            logger.debug(f"Ignoring non-Python file: {path}")
            return
        
        # Create FileEvent and add to queue
        file_event = FileEvent(
            path=path,
            event_type="saved" if event_type == "modified" else event_type,
            timestamp=datetime.now(),
        )
        
        # Requirement 1.3: Add to analysis queue
        self._analysis_queue.put(file_event)
        logger.debug(f"Queued Python file for analysis: {path}")
        
        # Trigger callback
        if self._callback:
            try:
                self._callback(file_event)
            except Exception as e:
                # Requirement 1.4: Log errors and continue
                logger.error(f"Error in callback for {path}: {e}")


def is_python_file(path: Path) -> bool:
    """Check if a file is a Python file.
    
    A file is considered a Python file if and only if it has
    a .py extension (case-insensitive).
    
    Args:
        path: Path to check
        
    Returns:
        True if the file has a .py extension, False otherwise
        
    Requirements: 1.1, 1.2
    """
    return path.suffix.lower() == ".py"


class FileWatcher:
    """Monitors a directory for Python file changes.
    
    Uses the watchdog library to watch for file system events
    and triggers analysis when Python files are saved.
    
    Attributes:
        analysis_queue: Queue of pending file events for analysis
        
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    
    def __init__(self) -> None:
        """Initialize the FileWatcher."""
        self._observer: Optional[Observer] = None
        self._callback: Optional[Callable[[FileEvent], None]] = None
        self._analysis_queue: queue.Queue[FileEvent] = queue.Queue()
        self._is_running = False
        self._lock = threading.Lock()
    
    @property
    def analysis_queue(self) -> "queue.Queue[FileEvent]":
        """Get the analysis queue.
        
        Returns:
            Queue containing pending FileEvents for analysis
            
        Requirements: 1.3
        """
        return self._analysis_queue
    
    def start(self, directory: Path) -> None:
        """Start watching the specified directory.
        
        Begins monitoring the directory for Python file changes.
        When a .py file is saved, the registered callback will be invoked.
        
        Args:
            directory: Path to the directory to monitor
            
        Raises:
            FileNotFoundError: If the directory does not exist
            NotADirectoryError: If the path is not a directory
            RuntimeError: If the watcher is already running
            
        Requirements: 1.1
        """
        with self._lock:
            if self._is_running:
                raise RuntimeError("FileWatcher is already running")
            
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            if not directory.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {directory}")
            
            # Create event handler
            handler = PythonFileHandler(
                callback=self._callback,
                analysis_queue=self._analysis_queue,
            )
            
            # Create and start observer
            self._observer = Observer()
            self._observer.schedule(handler, str(directory), recursive=True)
            self._observer.start()
            self._is_running = True
            
            logger.info(f"Started watching directory: {directory}")
    
    def stop(self) -> None:
        """Stop watching and clean up resources.
        
        Stops the file system observer and cleans up any resources.
        Safe to call even if the watcher is not running.
        """
        with self._lock:
            if self._observer is not None:
                self._observer.stop()
                self._observer.join(timeout=5.0)
                self._observer = None
                self._is_running = False
                logger.info("Stopped file watcher")
    
    def on_file_saved(self, callback: Callable[[FileEvent], None]) -> None:
        """Register a callback for file save events.
        
        The callback will be invoked whenever a Python file is saved
        in the monitored directory.
        
        Args:
            callback: Function to call with FileEvent when a .py file is saved
        """
        self._callback = callback
    
    def is_running(self) -> bool:
        """Check if the watcher is currently running.
        
        Returns:
            True if the watcher is actively monitoring, False otherwise
        """
        with self._lock:
            return self._is_running
    
    def get_pending_count(self) -> int:
        """Get the number of files pending analysis.
        
        Returns:
            Number of FileEvents in the analysis queue
            
        Requirements: 1.3
        """
        return self._analysis_queue.qsize()
    
    def get_next_pending(self, timeout: Optional[float] = None) -> Optional[FileEvent]:
        """Get the next file pending analysis.
        
        Args:
            timeout: Maximum time to wait for an event (None = non-blocking)
            
        Returns:
            The next FileEvent, or None if queue is empty
            
        Requirements: 1.3
        """
        try:
            if timeout is None:
                return self._analysis_queue.get_nowait()
            else:
                return self._analysis_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def clear_queue(self) -> int:
        """Clear all pending file events from the queue.
        
        Returns:
            Number of events that were cleared
        """
        count = 0
        while True:
            try:
                self._analysis_queue.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count
