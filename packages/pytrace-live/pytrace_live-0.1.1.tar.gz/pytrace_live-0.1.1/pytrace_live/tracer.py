"""Core tracing functionality."""

import sys
import time
from typing import Any, Dict, Optional

from rich.console import Console


class FunctionTracer:
    """Traces function execution times in real-time."""

    def __init__(self, threshold_ms: int = 100):
        """
        Initialize the tracer.

        Args:
            threshold_ms: Milliseconds threshold for marking functions as slow
        """
        self.threshold_ms = threshold_ms
        self.call_times: Dict[int, float] = {}
        self.console = Console()
        self.old_profile = None
        self.target_file = None

    def profile_callback(self, frame: Any, event: str, arg: Any) -> None:
        """
        Profile callback function for sys.setprofile.

        Args:
            frame: Current stack frame
            event: Event type ('call', 'return', etc.)
            arg: Event-specific argument
        """
        file_name = frame.f_code.co_filename
        func_name = frame.f_code.co_name

        # Skip if not from target file
        if self.target_file and file_name != self.target_file:
            return

        # Skip internal/system functions
        if self._should_skip(file_name, func_name):
            return

        if event == "call":
            frame_id = id(frame)
            self.call_times[frame_id] = time.perf_counter()

        elif event == "return":
            frame_id = id(frame)
            if frame_id in self.call_times:
                start_time = self.call_times.pop(frame_id)
                duration_ms = (time.perf_counter() - start_time) * 1000
                self._print_trace(func_name, duration_ms)

    def _should_skip(self, file_name: str, func_name: str) -> bool:
        """
        Determine if a function should be skipped from tracing.

        Args:
            file_name: File path of the function
            func_name: Name of the function

        Returns:
            True if function should be skipped
        """
        # Skip internal Python files
        if file_name.startswith("<"):
            return True

        # Skip pytrace_live itself
        if "pytrace_live" in file_name:
            return True

        # Skip rich library
        if "rich" in file_name or "site-packages" in file_name:
            return True

        # Skip standard library
        if "lib/python" in file_name or "lib\\python" in file_name:
            return True

        # Skip private functions (but allow __init__, __main__, etc.)
        if func_name.startswith("_") and func_name not in ("__init__", "__main__"):
            return True

        # Skip lambda and comprehensions
        if func_name in ("<lambda>", "<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>"):
            return True

        return False

    def _print_trace(self, func_name: str, duration_ms: float) -> None:
        """
        Print formatted trace output.

        Args:
            func_name: Name of the function
            duration_ms: Execution time in milliseconds
        """
        duration_str = f"{duration_ms:>6.0f} ms"

        if duration_ms >= self.threshold_ms * 5:
            status = "🚨 VERY SLOW"
            color = "red bold"
        elif duration_ms >= self.threshold_ms:
            status = "⚠ SLOW"
            color = "yellow"
        else:
            status = ""
            color = "green"

        output = f"→ {func_name:<25} {duration_str}"
        if status:
            output += f"  {status}"

        self.console.print(output, style=color, highlight=False)

    def start(self, target_file: Optional[str] = None) -> None:
        """
        Start profiling.

        Args:
            target_file: If provided, only trace functions from this file
        """
        self.target_file = target_file
        self.old_profile = sys.getprofile()
        sys.setprofile(self.profile_callback)

    def stop(self) -> None:
        """Stop profiling and restore previous profiler."""
        sys.setprofile(self.old_profile)