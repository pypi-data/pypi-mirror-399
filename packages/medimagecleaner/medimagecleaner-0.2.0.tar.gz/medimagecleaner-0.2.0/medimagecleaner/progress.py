"""
Progress Tracking Module

Provides progress bars and status updates for long-running operations.
"""

import time
from typing import Optional, Callable
from datetime import datetime, timedelta


class ProgressTracker:
    """Tracks and displays progress for batch operations."""
    
    def __init__(
        self,
        total: int,
        description: str = "Processing",
        show_eta: bool = True,
        show_percentage: bool = True,
        show_count: bool = True,
        bar_length: int = 40,
        update_interval: float = 0.1,
    ):
        """
        Initialize the progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the task
            show_eta: Show estimated time to completion
            show_percentage: Show percentage complete
            show_count: Show item count
            bar_length: Length of the progress bar
            update_interval: Minimum seconds between updates
        """
        self.total = total
        self.description = description
        self.show_eta = show_eta
        self.show_percentage = show_percentage
        self.show_count = show_count
        self.bar_length = bar_length
        self.update_interval = update_interval
        
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = 0
        self.completed = False
    
    def update(self, n: int = 1, force: bool = False):
        """
        Update progress.
        
        Args:
            n: Number of items completed
            force: Force display update even if interval hasn't passed
        """
        self.current += n
        
        current_time = time.time()
        if not force and (current_time - self.last_update_time) < self.update_interval:
            return
        
        self.last_update_time = current_time
        self._display()
    
    def _display(self):
        """Display the progress bar."""
        if self.total == 0:
            return
        
        # Calculate percentage
        percentage = (self.current / self.total) * 100
        
        # Create progress bar
        filled_length = int(self.bar_length * self.current // self.total)
        bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
        
        # Build status line
        status_parts = [f"\r{self.description}: [{bar}]"]
        
        if self.show_percentage:
            status_parts.append(f"{percentage:.1f}%")
        
        if self.show_count:
            status_parts.append(f"{self.current}/{self.total}")
        
        if self.show_eta and self.current > 0:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate
            eta = timedelta(seconds=int(remaining))
            status_parts.append(f"ETA: {eta}")
        
        # Print status
        print(" | ".join(status_parts), end='', flush=True)
    
    def finish(self):
        """Mark progress as complete."""
        self.current = self.total
        self._display()
        print()  # New line
        self.completed = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if not self.completed:
            self.finish()


class MultiProgressTracker:
    """Track progress for multiple concurrent operations."""
    
    def __init__(self):
        """Initialize the multi-progress tracker."""
        self.trackers = {}
        self.next_id = 0
    
    def create_tracker(
        self,
        total: int,
        description: str = "Processing",
        **kwargs
    ) -> int:
        """
        Create a new progress tracker.
        
        Args:
            total: Total number of items
            description: Task description
            **kwargs: Additional arguments for ProgressTracker
        
        Returns:
            Tracker ID
        """
        tracker_id = self.next_id
        self.next_id += 1
        
        self.trackers[tracker_id] = {
            "tracker": ProgressTracker(total, description, **kwargs),
            "description": description,
        }
        
        return tracker_id
    
    def update(self, tracker_id: int, n: int = 1):
        """Update a specific tracker."""
        if tracker_id in self.trackers:
            self.trackers[tracker_id]["tracker"].update(n)
    
    def finish(self, tracker_id: int):
        """Mark a tracker as complete."""
        if tracker_id in self.trackers:
            self.trackers[tracker_id]["tracker"].finish()
    
    def finish_all(self):
        """Mark all trackers as complete."""
        for tracker_id in self.trackers:
            self.finish(tracker_id)


class StatusLogger:
    """Logs status messages with timestamps and levels."""
    
    def __init__(
        self,
        show_timestamp: bool = True,
        show_level: bool = True,
    ):
        """
        Initialize the status logger.
        
        Args:
            show_timestamp: Include timestamps in messages
            show_level: Include log level in messages
        """
        self.show_timestamp = show_timestamp
        self.show_level = show_level
    
    def _format_message(self, level: str, message: str) -> str:
        """Format a log message."""
        parts = []
        
        if self.show_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"[{timestamp}]")
        
        if self.show_level:
            parts.append(f"[{level}]")
        
        parts.append(message)
        
        return " ".join(parts)
    
    def info(self, message: str):
        """Log an info message."""
        print(self._format_message("INFO", message))
    
    def success(self, message: str):
        """Log a success message."""
        print(self._format_message("✓ SUCCESS", message))
    
    def warning(self, message: str):
        """Log a warning message."""
        print(self._format_message("⚠ WARNING", message))
    
    def error(self, message: str):
        """Log an error message."""
        print(self._format_message("✗ ERROR", message))
    
    def debug(self, message: str):
        """Log a debug message."""
        print(self._format_message("DEBUG", message))


class Timer:
    """Simple timer for measuring operation duration."""
    
    def __init__(self, description: str = "Operation"):
        """
        Initialize the timer.
        
        Args:
            description: Description of the timed operation
        """
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        print(f"{self.description} started...")
    
    def stop(self) -> float:
        """
        Stop the timer and return elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        
        # Format elapsed time
        if elapsed < 60:
            time_str = f"{elapsed:.2f}s"
        elif elapsed < 3600:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            time_str = f"{minutes}m {seconds}s"
        else:
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            time_str = f"{hours}h {minutes}m"
        
        print(f"{self.description} completed in {time_str}")
        return elapsed
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def with_progress(
    items,
    description: str = "Processing",
    **kwargs
):
    """
    Iterator wrapper that shows progress.
    
    Args:
        items: Iterable to process
        description: Task description
        **kwargs: Additional arguments for ProgressTracker
    
    Yields:
        Items from the iterable
    """
    items_list = list(items)
    tracker = ProgressTracker(len(items_list), description, **kwargs)
    
    try:
        for item in items_list:
            yield item
            tracker.update()
    finally:
        tracker.finish()


# Example usage functions
def example_basic_progress():
    """Example: Basic progress bar."""
    import time
    
    tracker = ProgressTracker(
        total=100,
        description="Processing files"
    )
    
    for i in range(100):
        time.sleep(0.05)  # Simulate work
        tracker.update()
    
    tracker.finish()


def example_context_manager():
    """Example: Using context manager."""
    import time
    
    with ProgressTracker(50, "Downloading") as tracker:
        for i in range(50):
            time.sleep(0.05)
            tracker.update()


def example_with_progress_wrapper():
    """Example: Using with_progress wrapper."""
    import time
    
    files = range(30)
    for file in with_progress(files, "Processing"):
        time.sleep(0.05)  # Simulate work


def example_timer():
    """Example: Using timer."""
    import time
    
    with Timer("Large computation"):
        time.sleep(2)  # Simulate work


def example_status_logger():
    """Example: Using status logger."""
    logger = StatusLogger()
    
    logger.info("Starting process")
    logger.success("File processed successfully")
    logger.warning("Validation issues found")
    logger.error("Failed to process file")
